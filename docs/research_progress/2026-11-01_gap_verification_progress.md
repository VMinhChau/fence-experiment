# FENCE — Research Gap Verification and Current Status

**Date:** 2026-11-01
**Project:** Revocation That Sticks: Post-Acknowledgment Authority Revocation across Agent Memory, Caches, Branches, and Tool Queues

---

## 1. Executive Summary

Trong giai đoạn này, mục tiêu chính là kiểm chứng lại ba research gaps ban đầu của FENCE thông qua việc đối chiếu với các nghiên cứu liên quan, đặc biệt:

* **P1 — Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents.**
arXiv:2607.10487, July 2026.
* **P2 — Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution.**
arXiv:2609.21284, September 2026.

Kết quả cho thấy một số ý tưởng ban đầu của FENCE đã được prior work giải quyết hoặc đề cập đáng kể. Vì vậy, không nên tiếp tục xem các cơ chế như AND/OR dependency support, independent-support preservation hay ACK-after-fencing là novelty độc lập.

### Current gap status

| Gap   | Original research question                    | Verification result                                                                                                                                                 | Current status                |
| ----- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------- |
| Gap A | Artifact-level Dependency Semantics           | P2 đã có support antichain, AND/OR dependencies, independent-support preservation và rebind. Semantic provenance sau LLM transformation vẫn cần kiểm chứng sâu hơn. | Partially addressed           |
| Gap B | ACK Semantics and Writer Fencing              | P2 đã có root cut, sink barriers, carrier closure, channel reconciliation và quiescence certificate.                                                                | Not a standalone research gap |
| Gap C | Independent Benchmark for Post-ACK Revocation | P1/P2 đã bao phủ phần lớn các nhóm scenario ban đầu. Semantic correctness của recomputation dưới concurrent revocation vẫn là hướng cần kiểm chứng.                 | Partially addressed           |

**Overall conclusion:**

Chưa có research gap mới nào của FENCE được xác nhận đầy đủ.

Hướng tiếp theo nên chuyển từ việc mở rộng các scenario revocation sang kiểm chứng sâu hơn hai vấn đề:

1. Semantic authorization provenance after LLM transformation.
2. Correctness of derived-decision recomputation under concurrent revocation.

---

## 2. Gap A — Artifact-level Dependency Semantics

### 2.1. Original idea

FENCE ban đầu sử dụng support set để biểu diễn authorization dependencies của một artifact:

```python
AuthorityEpoch = Tuple[str, int]
SupportSet = Set[AuthorityEpoch]
```

Mỗi artifact lưu các cặp `(authority, epoch)` thể hiện những authorization mà artifact phụ thuộc vào.

Mục tiêu ban đầu:

* Biểu diễn dependency giữa artifact và authority.
* Phân biệt mandatory dependencies (AND) và alternative dependencies (OR).
* Khi một authority bị revoke, chỉ vô hiệu hóa những phần thực sự phụ thuộc vào authority đó.
* Bảo toàn những phần công việc vẫn có authorization hợp lệ.

### 2.2. Verification against prior work

#### P2

P2 đã đề cập trực tiếp đến:

* Support antichain.
* Conjunctive và alternative authorization support.
* Selected authorization witness.
* Independent-support preservation.
* Atomic rebind sang independent support còn hợp lệ.
* Parent-child provenance.

Do đó, các ý tưởng sau không còn đủ cơ sở để xem là novelty độc lập:

* AND/OR dependency representation.
* Independent-support preservation.
* Support propagation.
* Rebinding sang authorization còn hiệu lực.

P2 cũng yêu cầu support provenance phải đầy đủ và được xác thực theo giả định A4. Nếu provenance bị thiếu hoặc không rõ ràng, carrier được xem là unknown.

Cần lưu ý rằng P2 có thể biểu diễn claim-level dependencies nếu từng claim được đăng ký như một carrier và provenance chính xác được cung cấp. Không nên tuyên bố rằng P2 hoàn toàn không hỗ trợ claim-level provenance.

#### P1

P1 sử dụng dependency evidence kết nối:

```text
Authority Witness
       |
       v
   Derived State
       |
       v
   Durable Effect
```

CommitGuard kiểm tra dependency evidence tại commit time.

P1 không yêu cầu phải lưu toàn bộ reasoning chain của LLM, nhưng cần runtime cung cấp đủ dependency evidence để kiểm tra authorization. Những dependency bị ẩn hoặc không được ghi nhận nằm ngoài phạm vi bảo đảm.

### 2.3. Remaining research question

Vấn đề cần kiểm chứng sâu hơn:

**Semantic authorization provenance after LLM transformation.**

Ví dụ:

1. Agent nhận nhiều evidence từ các authority khác nhau.
2. Agent tổng hợp evidence thành summary hoặc decision.
3. Kết quả có nhiều claims với các dependency khác nhau.
4. Một số authority bị revoke.
5. Hệ thống phải xác định claim nào còn hợp lệ và claim nào cần được tái tạo.

Thách thức không chỉ nằm ở việc lưu support set cho toàn bộ artifact, mà còn ở việc xác định và duy trì chính xác dependency ở mức claim qua các thao tác:

* Summarization.
* Paraphrasing.
* Aggregation.
* Memory consolidation.
* Derived-decision generation.

Cần tiếp tục kiểm tra liệu các phương pháp provenance hiện có như PACMI, Memory Provenance Laundering, GenProve và AuthGraph đã giải quyết đủ vấn đề này hay chưa.

### 2.4. Current status

**Partially addressed by prior work.**

| Sub-problem                                  | Status                        |
| -------------------------------------------- | ----------------------------- |
| AND/OR dependency representation             | Addressed by P2               |
| Independent-support preservation             | Addressed by P2               |
| Support propagation and rebind               | Addressed by P2               |
| Dependency evidence at commit time           | Addressed by P1               |
| Semantic provenance after LLM transformation | Requires further verification |

**Decision:** Không tiếp tục sử dụng AND/OR support hoặc independent-support preservation làm novelty chính. Tiếp tục kiểm chứng semantic provenance sau LLM transformation.

---

## 3. Gap B — ACK Semantics and Writer Fencing

### 3.1. Original idea

FENCE ban đầu đặt ra thuộc tính:

> After revocation is acknowledged, no subsequently committed operation may depend on revoked authorization.

Cơ chế dự kiến:

1. Advance authority epoch.
2. Publish revocation frontier.
3. Fence relevant writers.
4. Validate artifact support at commit time.
5. Acknowledge revocation only after the required fencing conditions are satisfied.

Mục tiêu là ngăn những operation được tạo dưới authorization cũ tiếp tục tạo ra durable effects sau revoke ACK.

### 3.2. Verification against prior work

#### P2

P2 đã xây dựng một protocol root-scoped quiescence gồm:

* Root cut.
* Sink-level durable barriers.
* Carrier closure.
* Channel reconciliation.
* Quiescence certificate.

Một điểm quan trọng cần phân biệt:

**Root cut is not equivalent to Quiescence ACK.**

Root cut chỉ retire authorization epoch cũ và ngăn việc cấp quyền mới từ epoch đó.

Quiescence certificate chỉ được cấp sau khi các sink barriers, carrier closure, channel reconciliation và các điều kiện bằng chứng liên quan đã được đáp ứng.

P2 cũng xét các tình huống như:

* Delegated tasks.
* Asynchronous execution.
* In-flight tokens.
* Stale processes.
* Restart and replay.
* Opaque endpoints.
* Missing sink fences.

#### P1

P1 đã nghiên cứu:

* Commit-time authorization.
* Authority witness freshness.
* Dependency validation.
* Effect binding.
* Commit eligibility.
* CommitGuard tại protected commit boundary.

P1 cũng đề cập việc revalidate, rebind, replan hoặc abort khi authorization witness không còn hợp lệ.

### 3.3. Verification result

Các ý tưởng sau không còn đủ cơ sở để xem là research gap độc lập:

* ACK only after writer fencing.
* Commit-time authorization validation.
* Epoch-based revocation.
* Sink-level enforcement.
* Blocking stale authorization at commit.

FENCE vẫn có thể nghiên cứu một cách triển khai đơn giản hơn hoặc ít overhead hơn. Tuy nhiên, khi đó cần chứng minh bằng thực nghiệm:

* Revocation latency.
* Commit validation overhead.
* Runtime complexity.
* Enforcement coverage.
* Preservation of valid operations.

Đây là những câu hỏi về hiệu quả và trade-off triển khai, không tự động tạo thành novelty về cơ chế.

### 3.4. Current status

**Not a standalone research gap.**

| Sub-problem                          | Status          |
| ------------------------------------ | --------------- |
| Epoch retirement                     | Addressed by P2 |
| Sink-level fencing                   | Addressed by P2 |
| Commit-time authorization validation | Addressed by P1 |
| Carrier and channel closure          | Addressed by P2 |
| ACK after quiescence conditions      | Addressed by P2 |

**Decision:** Loại Gap B khỏi danh sách novelty độc lập. Giữ các cơ chế này làm nền tảng kỹ thuật và baseline khi đánh giá FENCE.

---

## 4. Gap C — Independent Benchmark for Post-ACK Revocation

### 4.1. Original idea

FENCE được thiết kế với bảy nhóm scenario:

| ID | Scenario                   | Number | Expected property                                                              |
| -- | -------------------------- | -----: | ------------------------------------------------------------------------------ |
| F1 | Cache hit post-revocation  |     28 | Không sử dụng cached state phụ thuộc authority đã revoke để tạo commit sau ACK |
| F2 | Delayed tool call          |     26 | Ngăn delayed tool operation sử dụng authorization đã hết hiệu lực              |
| F3 | Offline agent returns      |     22 | Ngăn agent offline sử dụng stale state hoặc kết quả được tạo dưới authority cũ |
| F4 | Crash / restart            |     20 | Duy trì revocation frontier qua restart                                        |
| F5 | Branch rebase              |     24 | Ngăn artifact hết hiệu lực được đưa trở lại qua branch rebase                  |
| F6 | Independent corroboration  |     18 | Bảo toàn evidence và kết quả độc lập còn hợp lệ                                |
| F7 | Clean maintenance rotation |     12 | Bảo toàn công việc hợp lệ trong quá trình authorization rotation bình thường   |

**Total: 150 scenarios**

* Violation cases (F1–F5): 120.
* Preservation cases (F6–F7): 30.

### 4.2. Verification against P1

P1 có benchmark:

* 54 tasks.
* 270 runs.
* 18 browser tasks.
* 18 tool/state tasks.
* 18 multi-agent tasks.

Các hazard được nghiên cứu:

* Observation-to-action drift.
* Validation-to-commit drift.
* Out-of-order dependency.
* Speculative side-effect leakage.
* Stale visibility/shared-state skew.

P1 đã đề cập các tình huống liên quan đến cache, shared memory, speculative branches, delayed callbacks, worker outputs và tool writes.

### 4.3. Verification against P2

P2 có:

* 17 registered scenarios.
* 44 semantic mutants.

Các trường hợp liên quan đến FENCE:

* Root cut without sink fence.
* Root cut plus sink fence.
* Restart/stale process.
* Alternate-root rebind.
* Opaque endpoint/missing fence.
* In-flight token.
* Conjunctive witness.
* Ghost token.
* Terminal channel reopen.

P2 còn kiểm tra các thuộc tính như:

* Independent-support preservation.
* Merge-order independence.
* Crash/replay stability.
* Channel accounting.
* Root-scoped quiescence.

### 4.4. Scenario-level assessment

| FENCE scenario                  | Prior-work coverage                                               | Assessment                               |
| ------------------------------- | ----------------------------------------------------------------- | ---------------------------------------- |
| F1 — Cache hit post-revocation  | P1/P2 đề cập cache và stale shared state                          | Không phải novelty độc lập               |
| F2 — Delayed tool call          | P1/P2 đề cập delayed execution và asynchronous channels           | Không phải novelty độc lập               |
| F3 — Offline agent returns      | P2 đề cập stale process, carrier closure và restart-related cases | Cần kiểm tra mức tương đương cụ thể      |
| F4 — Crash / restart            | P2 đề cập crash/replay stability và restart                       | Không phải novelty độc lập               |
| F5 — Branch rebase              | P1/P2 đề cập speculative branches, merge và support propagation   | Không phải novelty độc lập               |
| F6 — Independent corroboration  | P2 có independent-support preservation và rebind                  | Không phải novelty độc lập ở mức cơ chế  |
| F7 — Clean maintenance rotation | Có liên quan đến preservation và independent authorization        | Cần xác định metric và phạm vi khác biệt |

Lưu ý: Prior-work coverage không đồng nghĩa với việc hai benchmark hoàn toàn giống nhau. Cần so sánh scenario preconditions, execution traces, expected outcomes và evaluation oracle trước khi kết luận hai trường hợp tương đương.

### 4.5. Remaining research question

Hướng cần kiểm chứng sâu hơn:

**Correctness of derived-decision recomputation under concurrent revocation.**

Ví dụ:

* Một decision được tạo từ nhiều evidence.
* Authority A bị revoke trong khi decision đang được tính toán.
* Hệ thống phải tính lại decision từ evidence còn hợp lệ.
* Trong lúc recomputation đang diễn ra, authority B tiếp tục bị revoke.
* Decision mới phải kiểm tra authorization state mới nhất trước khi commit.
* Một decision độc lập chỉ phụ thuộc vào authority C vẫn phải được bảo toàn.

Câu hỏi nghiên cứu:

1. Recomputed decision có chỉ sử dụng evidence còn được phép hay không?
2. Authorization state có được kiểm tra lại tại thời điểm commit hay không?
3. Một revoke mới trong quá trình recomputation có làm decision vừa tính xong trở nên stale hay không?
4. Independent work có được bảo toàn mà không cần reset toàn bộ agent state hay không?

Cần đối chiếu hướng này với:

* P1: CommitGuard, replan và eligibility recomputation.
* P2: Support rebind và independent-support preservation.
* Selective replay: Provenance-guided replay để tái tạo execution state và derived artifacts.

Chưa có bằng chứng thực nghiệm cho thấy việc kết hợp các phương pháp này không giải quyết được vấn đề.

### 4.6. Current status

**Partially addressed by prior work.**

| Sub-problem                                                       | Status                             |
| ----------------------------------------------------------------- | ---------------------------------- |
| Cache and stale state scenarios                                   | Covered in prior work              |
| Delayed tool execution                                            | Covered in prior work              |
| Crash/restart                                                     | Covered in P2                      |
| Branch and merge behavior                                         | Covered in prior work              |
| Independent-support preservation                                  | Addressed by P2                    |
| Semantic correctness of recomputation under concurrent revocation | Requires experimental verification |

**Decision:** Không tiếp tục xem việc có 150 scenario hoặc các tình huống F1–F7 riêng lẻ là novelty chính. Chuyển trọng tâm sang semantic correctness và preservation trong quá trình recomputation.

---

## 5. CEDAR-01 — Candidate Counterexample

### 5.1. Scenario

**CEDAR-01: Revocation During In-flight Derived Decision**

Giả sử hệ thống có:

```text
Evidence:
    E_A supported by Authority A
    E_B supported by Authority B
    E_C supported by Authority C

Decisions:
    D1 = f(E_A, E_B, E_C)
    D2 = g(E_C)
```

Trong đó:

* D1 phụ thuộc vào ba evidence.
* D2 chỉ phụ thuộc vào E_C.
* Các evidence có authorization support độc lập.

### 5.2. Execution sequence

| Step | Event                                                   | Expected behavior                        |
| ---- | ------------------------------------------------------- | ---------------------------------------- |
| 1    | Agent bắt đầu tính D1 từ E_A, E_B, E_C                  | D1 đang được xử lý                       |
| 2    | Authority A bị revoke                                   | Epoch của A được retire                  |
| 3    | Revocation ACK được phát hành                           | Các commit phụ thuộc A phải bị chặn      |
| 4    | D1 cũ thử commit                                        | Reject                                   |
| 5    | Hệ thống recompute D1 từ E_B, E_C                       | Tạo candidate mới                        |
| 6    | Authority B bị revoke trong khi recomputation đang chạy | Candidate mới có thể trở nên stale       |
| 7    | Candidate D1 mới thử commit                             | Phải validate lại theo frontier mới nhất |
| 8    | D2 tiếp tục hoạt động                                   | Phải được bảo toàn vì chỉ phụ thuộc E_C  |

### 5.3. Properties under test

1. **Post-ACK commit safety:** Không commit operation phụ thuộc vào authority đã revoke sau ACK.
2. **Selective recalculation:** Có thể tạo lại decision từ evidence còn hợp lệ.
3. **Independent-work preservation:** Không hủy D2 nếu dependency của nó vẫn hợp lệ.
4. **Latest-state validation:** Candidate phải được kiểm tra theo authorization frontier mới nhất tại commit time.

### 5.4. Why this scenario matters

CEDAR-01 kết hợp các vấn đề:

* Concurrent revocation.
* In-flight computation.
* Derived-decision recomputation.
* Independent evidence preservation.
* Commit-time validation.

Đây là candidate scenario có giá trị để kiểm tra giới hạn của các phương pháp hiện có.

Tuy nhiên, CEDAR-01 hiện mới là scenario được thiết kế, chưa phải counterexample đã được thực nghiệm xác nhận.

P1 có replan/repair và eligibility recomputation. P2 có support rebind. Selective replay có thể tái tạo execution state và derived artifacts.

Do đó, cần kiểm tra xem các phương pháp này khi kết hợp có giải quyết đầy đủ CEDAR-01 hay không.

---

## 6. Additional Verification of Core FENCE Mechanisms

Ngoài các research gaps đã phân tích, cần kiểm chứng riêng ba cơ chế kỹ thuật cốt lõi trong thiết kế FENCE.

| FENCE mechanism            | Relevant prior work | Verification result                                                                                       | Novelty status       |
| -------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------- | -------------------- |
| Merge-frontier propagation | P2                  | P2 đã đề cập compositional frontier certificates, merge-order independence và channel accounting.         | Prior work addressed |
| Commit-time re-validation  | P1, P2              | P1 có CommitGuard và commit-time witness validation; P2 có sink-level enforcement và support validation.  | Prior work addressed |
| Fence-before-acknowledge   | P2                  | P2 yêu cầu sink barriers, carrier closure và channel reconciliation trước khi cấp quiescence certificate. | Prior work addressed |

---

## 7. Overall Research Progress

### 7.1. Completed work

Các công việc đã hoàn thành ở mức phân tích tài liệu:

* Đọc và phân tích P1 về commit-time authorization.
* Đọc và phân tích P2 về root-scoped authorization quiescence.
* Đối chiếu AND/OR dependency support.
* Đối chiếu independent-support preservation.
* Đối chiếu ACK semantics và sink-level fencing.
* So sánh phạm vi benchmark P1/P2 với bảy nhóm scenario F1–F7 của FENCE.
* Xác định những ý tưởng ban đầu không còn đủ cơ sở để xem là novelty độc lập.
* Xây dựng candidate scenario CEDAR-01.

### 7.2. Not completed

Các công việc chưa được thực hiện:

* Xác minh đầy đủ semantic provenance sau LLM transformation.
* Chuyển CEDAR-01 thành runnable execution trace.
* Chạy baseline tương đương P1/P2 trên cùng scenario.
* Kiểm tra composition của replan/repair, support rebind và selective replay.
* Xây dựng independent oracle để kiểm tra correctness của recomputation.
* Chạy thực nghiệm trên 150 scenario.
* Đo violation rate, preservation rate và runtime overhead.

### 7.3. Important distinction

Các số liệu sau hiện chỉ là quy mô scenario hoặc kế hoạch đánh giá:

* 150 designed scenarios.
* 120 violation scenarios.
* 30 preservation scenarios.

Chúng không phải số lượng test đã chạy.

Các violation rates và preservation rates được đề xuất trong những bản nháp trước cũng chưa phải kết quả thực nghiệm. Chỉ cập nhật kết quả sau khi có execution logs, baseline outputs và kết quả kiểm tra độc lập.

---

## 8. Next Research Direction

Dựa trên kết quả kiểm chứng, đề xuất thứ tự công việc tiếp theo như sau.

### Phase 1 — Verify Semantic Provenance

**Objective:** Xác định liệu semantic authorization provenance sau LLM transformation có phải vấn đề chưa được giải quyết đầy đủ hay không.

Tasks:

1. Đọc sâu PACMI.
2. Đọc sâu Memory Provenance Laundering.
3. Đọc GenProve và AuthGraph để xác định phạm vi provenance được hỗ trợ.
4. Xây dựng ví dụ gồm nhiều evidence và nhiều output claims.
5. Kiểm tra cách provenance được duy trì qua summarization, aggregation và memory consolidation.
6. Xác định rõ khác biệt giữa provenance generation, provenance preservation và authorization validation.

Expected output:

* Related-work comparison.
* Claim-level provenance model.
* Danh sách các trường hợp provenance bị thiếu, sai hoặc không thể xác định.
* Kết luận liệu vấn đề này có đủ cơ sở làm research gap hay không.

### Phase 2 — Formalize CEDAR-01

**Objective:** Chuyển CEDAR-01 thành một execution trace có thể chạy và đánh giá.

Tasks:

1. Định nghĩa authority, evidence và decision.
2. Định nghĩa authorization frontier.
3. Định nghĩa dependency support của từng decision.
4. Xác định các event: compute, revoke, ACK, recompute và commit.
5. Định nghĩa expected outcomes.
6. Xây dựng oracle độc lập để kiểm tra safety và preservation.

Expected output:

* Runnable CEDAR-01 scenario.
* Event trace.
* Expected-state oracle.
* Test cases cho concurrent revocation.

### Phase 3 — Baseline Comparison

**Objective:** Kiểm tra liệu các cơ chế hiện có có giải quyết được CEDAR-01 hay không.

Các baseline cần so sánh:

| Baseline                       | Mechanism                                           |
| ------------------------------ | --------------------------------------------------- |
| B0 — Naive execution           | Không có cơ chế bảo vệ bổ sung tại commit           |
| B1 — Commit-time validation    | Kiểm tra authorization tại commit, theo hướng P1    |
| B2 — Support rebind/quiescence | Sử dụng các cơ chế tương ứng P2                     |
| B3 — Selective replay          | Tái tạo execution state sau khi dependency thay đổi |
| B4 — Combined baseline         | Kết hợp các cơ chế hiện có khi khả thi              |
| FENCE                          | Cơ chế FENCE được đề xuất                           |

Không nên giả định baseline nào thất bại trước khi chạy thực nghiệm.

Expected output:

* Violation comparison.
* Preservation comparison.
* Recalculation correctness.
* Runtime overhead.
* Failure analysis.

### Phase 4 — Reassess FENCE Contribution

Sau khi hoàn thành baseline comparison, cần trả lời:

1. Các phương pháp hiện có đã giải quyết đầy đủ CEDAR-01 chưa?
2. Nếu chưa, chúng thất bại ở điều kiện hoặc thuộc tính nào?
3. FENCE có cơ chế mới thực sự hay chỉ là cách kết hợp các cơ chế đã biết?
4. Nếu chỉ là combination, liệu có đóng góp thực nghiệm hoặc hệ thống đủ rõ ràng không?
5. Phạm vi bảo đảm của FENCE khác gì so với P1 và P2?

Chỉ sau bước này mới nên chốt research gap và contribution claims.

---

## 9. Current Research Position

Tại thời điểm 2026-11-01, định hướng FENCE nên được cập nhật:

| Component                                    | Decision                                                      |
| -------------------------------------------- | ------------------------------------------------------------- |
| Artifact-level support semantics             | Sử dụng làm nền tảng, không tuyên bố novelty độc lập          |
| AND/OR dependency                            | Đã có prior work                                              |
| Independent-support preservation             | Đã có prior work                                              |
| Merge-frontier propagation                   |Đã có prior work                                              |
| ACK-after-fencing                            | Không dùng làm novelty độc lập                                |
| Commit-time validation                       | Đã có prior work                                              |
| F1–F7 benchmark scenarios                    | Giữ làm evaluation scenarios, không tuyên bố từng nhóm là mới |
| Semantic provenance after LLM transformation | Tiếp tục kiểm chứng                                           |
| Concurrent derived-decision recomputation    | Ưu tiên kiểm chứng bằng CEDAR-01                              |

### Final assessment

FENCE hiện chưa có research gap mới được xác nhận đầy đủ. Tuy nhiên, quá trình đối chiếu P1 và P2 đã giúp thu hẹp phạm vi nghiên cứu và loại bỏ những novelty claims không còn đủ cơ sở.

**Hướng ưu tiên tiếp theo là kiểm chứng correctness của derived-decision recomputation dưới concurrent revocation, sử dụng CEDAR-01 và các baseline từ P1, P2 và selective replay.**

Mục tiêu không phải chứng minh FENCE tốt hơn bằng cách tạo thêm nhiều scenario, mà là xác định chính xác một vấn đề mà các phương pháp hiện có chưa giải quyết thỏa đáng, nếu vấn đề đó thực sự tồn tại.
