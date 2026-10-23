// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract PayPulse is Ownable, ReentrancyGuard {
    using SafeERC20 for IERC20;

    error BudgetExceeded(uint256 spent, uint256 allocation);
    error NotProxy();
    error AgentNotActive();
    error AlreadyVoted();
    error NotApprover();
    error RequestNotPending();
    error InsufficientPool();
    error ZeroAddress();
    error InvalidBps();
    error AgentAlreadyExists();

    event Deposit(address indexed depositor, uint256 amount, uint256 newPoolBalance);
    event AgentAdded(address indexed agent, uint256 allocationBps, uint256 periodLength);
    event AgentRemoved(address indexed agent);
    event Draw(address indexed agent, uint256 amount, uint256 spent, uint256 allocation);
    event Disbursed(address indexed to, uint256 amount, address indexed agent);
    event PeriodReset(address indexed agent, uint256 newAllocation, uint256 timestamp);
    event BorrowRequested(uint256 indexed requestId, address indexed agent, uint256 amount, string reason);
    event BorrowApproved(uint256 indexed requestId, address indexed agent, uint256 amount, string reason, bool autoApproved);
    event BorrowRejected(uint256 indexed requestId, address indexed agent, uint256 amount);
    event ProxySet(address indexed proxy);
    event ApproverAdded(address indexed approver);
    event ApproverRemoved(address indexed approver);

    uint256 public constant BORROW_THRESHOLD_BPS = 5_000;
    uint256 public constant REQUIRED_APPROVALS = 2;

    IERC20 public immutable usdc;
    address public proxy;

    uint256 public poolBalance;
    uint256 public totalAllocBps;

    struct Agent {
        uint256 allocationBps;
        uint256 periodStart;
        uint256 periodLength;
        uint256 allocation;
        uint256 spent;
        bool isLender;
        uint256 maxLendBps;
        bool active;
    }

    mapping(address => Agent) public agents;
    address[] public agentList;

    enum BorrowStatus {
        Pending,
        Approved,
        Rejected
    }

    struct BorrowRequest {
        uint256 id;
        address agent;
        uint256 amount;
        string reason;
        BorrowStatus status;
        uint256 approvals;
        uint256 rejections;
    }

    uint256 public borrowRequestCount;
    mapping(uint256 => BorrowRequest) public borrowRequestsById;
    uint256[] public pendingRequestIds;
    mapping(uint256 => mapping(address => bool)) public borrowVoted;

    mapping(address => bool) public approvers;
    address[] public approverList;

    modifier onlyProxy() {
        if (msg.sender != proxy) revert NotProxy();
        _;
    }

    modifier onlyApprover() {
        if (!approvers[msg.sender]) revert NotApprover();
        _;
    }

    constructor(address usdcToken, address initialOwner) Ownable(initialOwner) {
        if (usdcToken == address(0) || initialOwner == address(0)) revert ZeroAddress();
        usdc = IERC20(usdcToken);
    }

    function setProxy(address newProxy) external onlyOwner {
        if (newProxy == address(0)) revert ZeroAddress();
        proxy = newProxy;
        emit ProxySet(newProxy);
    }

    function deposit(uint256 amount) external nonReentrant {
        usdc.safeTransferFrom(msg.sender, address(this), amount);
        poolBalance += amount;
        emit Deposit(msg.sender, amount, poolBalance);
    }

    function addAgent(
        address agent,
        uint256 allocationBps,
        uint256 periodLength,
        bool isLender,
        uint256 maxLendBps
    ) external onlyOwner {
        if (agent == address(0)) revert ZeroAddress();
        if (agents[agent].active) revert AgentAlreadyExists();
        if (allocationBps == 0 || maxLendBps > 10_000) revert InvalidBps();

        uint256 newTotal = totalAllocBps + allocationBps;
        if (newTotal > 10_000) revert InvalidBps();

        uint256 allocation = (poolBalance * allocationBps) / 10_000;
        // Reserve the initial allocation from the pool so poolBalance tracks
        // only USDC that is unallocated and truly available to the pool.
        if (allocation > poolBalance) revert InsufficientPool();
        poolBalance -= allocation;

        agents[agent] = Agent({
            allocationBps: allocationBps,
            periodStart: block.timestamp,
            periodLength: periodLength,
            allocation: allocation,
            spent: 0,
            isLender: isLender,
            maxLendBps: maxLendBps,
            active: true
        });

        totalAllocBps = newTotal;
        agentList.push(agent);

        emit AgentAdded(agent, allocationBps, periodLength);
    }

    function removeAgent(address agent) external onlyOwner {
        Agent storage a = agents[agent];
        if (!a.active) revert AgentNotActive();

        // Return unspent reserved allocation back to the free pool
        uint256 unreserved = a.allocation > a.spent ? a.allocation - a.spent : 0;
        poolBalance += unreserved;

        totalAllocBps -= a.allocationBps;
        a.active = false;

        uint256 len = agentList.length;
        for (uint256 i = 0; i < len; ++i) {
            if (agentList[i] == agent) {
                agentList[i] = agentList[len - 1];
                agentList.pop();
                break;
            }
        }

        emit AgentRemoved(agent);
    }

    /// @notice Transfer USDC out of the treasury to a recipient.
    /// Only callable by the authorized proxy. The proxy must have already
    /// called draw() to charge the agent's budget before calling disburse().
    function disburse(address to, uint256 amount, address agent) external onlyProxy nonReentrant {
        if (to == address(0)) revert ZeroAddress();
        usdc.safeTransfer(to, amount);
        emit Disbursed(to, amount, agent);
    }

    function draw(address agent, uint256 amount) external onlyProxy {
        _maybeResetPeriod(agent);

        Agent storage a = agents[agent];
        if (!a.active) revert AgentNotActive();

        uint256 newSpent = a.spent + amount;
        // agent.allocation is the reserved budget; poolBalance tracks free USDC.
        // draw() marks reserved funds as spent — no further poolBalance deduction.
        if (newSpent > a.allocation) revert BudgetExceeded(newSpent, a.allocation);

        a.spent = newSpent;

        emit Draw(agent, amount, a.spent, a.allocation);
    }

    function resetPeriod(address agentAddr) external {
        _maybeResetPeriod(agentAddr);
    }

    function requestBorrow(address agentAddr, uint256 amount, string calldata reason) external {
        // Only the agent itself, the owner, or the proxy may file a borrow request
        if (msg.sender != agentAddr && msg.sender != owner() && msg.sender != proxy) revert AgentNotActive();

        _maybeResetPeriod(agentAddr);

        Agent storage a = agents[agentAddr];
        if (!a.active) revert AgentNotActive();

        uint256 threshold = (a.allocation * BORROW_THRESHOLD_BPS) / 10_000;

        if (amount <= threshold) {
            if (_executeBorrow(agentAddr, amount)) {
                emit BorrowApproved(0, agentAddr, amount, reason, true);
                return;
            }
        }

        uint256 id = ++borrowRequestCount;
        borrowRequestsById[id] = BorrowRequest({
            id: id,
            agent: agentAddr,
            amount: amount,
            reason: reason,
            status: BorrowStatus.Pending,
            approvals: 0,
            rejections: 0
        });
        pendingRequestIds.push(id);

        emit BorrowRequested(id, agentAddr, amount, reason);
    }

    function approveBorrow(uint256 requestId) external onlyApprover {
        BorrowRequest storage req = borrowRequestsById[requestId];
        if (req.status != BorrowStatus.Pending) revert RequestNotPending();
        if (borrowVoted[requestId][msg.sender]) revert AlreadyVoted();

        borrowVoted[requestId][msg.sender] = true;
        req.approvals += 1;

        if (req.approvals >= REQUIRED_APPROVALS) {
            if (!_executeBorrow(req.agent, req.amount)) revert InsufficientPool();

            req.status = BorrowStatus.Approved;
            _removePendingId(requestId);

            emit BorrowApproved(requestId, req.agent, req.amount, req.reason, false);
        }
    }

    function rejectBorrow(uint256 requestId) external onlyApprover {
        BorrowRequest storage req = borrowRequestsById[requestId];
        if (req.status != BorrowStatus.Pending) revert RequestNotPending();
        if (borrowVoted[requestId][msg.sender]) revert AlreadyVoted();

        borrowVoted[requestId][msg.sender] = true;
        req.rejections += 1;

        if (req.rejections >= REQUIRED_APPROVALS) {
            req.status = BorrowStatus.Rejected;
            _removePendingId(requestId);

            emit BorrowRejected(requestId, req.agent, req.amount);
        }
    }

    function addApprover(address approver) external onlyOwner {
        if (approver == address(0)) revert ZeroAddress();
        if (approvers[approver]) return;
        // Enforce exactly 3 approvers for the 2-of-3 multisig semantics
        if (approverList.length >= 3) revert InvalidBps();

        approvers[approver] = true;
        approverList.push(approver);

        emit ApproverAdded(approver);
    }

    function removeApprover(address approver) external onlyOwner {
        if (!approvers[approver]) return;

        approvers[approver] = false;

        uint256 len = approverList.length;
        for (uint256 i = 0; i < len; ++i) {
            if (approverList[i] == approver) {
                approverList[i] = approverList[len - 1];
                approverList.pop();
                break;
            }
        }

        emit ApproverRemoved(approver);
    }

    function getAgentInfo(
        address agentAddr
    )
        external
        view
        returns (
            uint256 allocationBps,
            uint256 periodStart,
            uint256 periodLength,
            uint256 allocation,
            uint256 spent,
            bool isLender,
            uint256 maxLendBps,
            bool active
        )
    {
        Agent storage a = agents[agentAddr];
        return (
            a.allocationBps,
            a.periodStart,
            a.periodLength,
            a.allocation,
            a.spent,
            a.isLender,
            a.maxLendBps,
            a.active
        );
    }

    function getPendingRequests() external view returns (uint256[] memory) {
        return pendingRequestIds;
    }

    function getBorrowRequest(
        uint256 id
    )
        external
        view
        returns (
            uint256 requestId,
            address agent,
            uint256 amount,
            string memory reason,
            BorrowStatus status,
            uint256 approvals,
            uint256 rejections
        )
    {
        BorrowRequest storage req = borrowRequestsById[id];
        return (req.id, req.agent, req.amount, req.reason, req.status, req.approvals, req.rejections);
    }

    function getAgentList() external view returns (address[] memory) {
        return agentList;
    }

    function getApproverList() external view returns (address[] memory) {
        return approverList;
    }

    /// @notice Total USDC held by the contract (free pool + all reserved allocations)
    function totalHeld() external view returns (uint256) {
        return usdc.balanceOf(address(this));
    }

    function _maybeResetPeriod(address agentAddr) internal {
        Agent storage a = agents[agentAddr];
        if (!a.active) return;

        if (block.timestamp >= a.periodStart + a.periodLength) {
            // Return unspent portion of current allocation back to the free pool.
            // (allocated funds were deducted from poolBalance when assigned)
            uint256 unspent = a.allocation > a.spent ? a.allocation - a.spent : 0;
            poolBalance += unspent;

            // Recalculate the new allocation from the refreshed pool balance.
            uint256 newAlloc = (poolBalance * a.allocationBps) / 10_000;
            // Reserve the new allocation from the pool.
            if (newAlloc > poolBalance) newAlloc = poolBalance;
            poolBalance -= newAlloc;

            a.allocation = newAlloc;
            a.periodStart = block.timestamp;
            a.spent = 0;

            emit PeriodReset(agentAddr, a.allocation, block.timestamp);
        }
    }

    function _executeBorrow(address agentAddr, uint256 amount) internal returns (bool) {
        if (poolBalance >= amount) {
            poolBalance -= amount;
            agents[agentAddr].allocation += amount;
            return true;
        }

        return _tryBorrowFromLender(agentAddr, amount);
    }

    function _tryBorrowFromLender(address borrower, uint256 amount) internal returns (bool) {
        uint256 len = agentList.length;

        for (uint256 i = 0; i < len; ++i) {
            address lenderAddr = agentList[i];
            if (lenderAddr == borrower) continue;

            Agent storage lender = agents[lenderAddr];
            if (!lender.active || !lender.isLender) continue;

            uint256 maxLend = (lender.allocation * lender.maxLendBps) / 10_000;
            uint256 lendable = maxLend > lender.spent ? maxLend - lender.spent : 0;

            if (lendable >= amount && lender.allocation >= amount) {
                lender.allocation -= amount;
                agents[borrower].allocation += amount;
                return true;
            }
        }

        return false;
    }

    function _removePendingId(uint256 id) internal {
        uint256 len = pendingRequestIds.length;
        for (uint256 i = 0; i < len; ++i) {
            if (pendingRequestIds[i] == id) {
                pendingRequestIds[i] = pendingRequestIds[len - 1];
                pendingRequestIds.pop();
                break;
            }
        }
    }
}
