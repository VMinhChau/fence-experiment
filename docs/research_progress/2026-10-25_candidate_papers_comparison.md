# Candidate Papers Comparison

## 1. Candidate Papers

1. **Temporary Authority, Permanent Effects: Commit-Time Authorization for LLM Agents**

   https://arxiv.org/pdf/2607.10487
2. **Authorization Revocation for Long-Running AI Agents: Root-Scoped Quiescence under Delegation and Asynchronous Execution**

   https://arxiv.org/pdf/2609.21284
3. **ResidualAuth: What Authorization State Must Language Agents Preserve under Revocable Delegation?**

   https://arxiv.org/pdf/2609.08062

Hai bài 1 và 2 được chọn để phân tích chuyên sâu vì có sự giao thoa lớn với FENCE về authorization revocation, dependency tracking và ngăn các thao tác tạo hiệu ứng dựa trên authority đã bị thu hồi. Bài thứ ba, ResidualAuth, có thể được xem xét bổ sung vì liên quan đến việc duy trì thông tin authorization cần thiết để quyết định vẫn đúng sau khi quyền bị thu hồi. ResidualAuth trùng lặp với FENCE ở mức đáng kể về vấn đề authorization sau revoke, nhưng không trùng hoàn toàn về cơ chế và mục tiêu nghiên cứu.

## 2. Những điểm trùng lặp chính giữa các công trình và FENCE

### 2.1. Cùng quan tâm đến việc authorization cũ không được tiếp tục tạo ra hiệu ứng mới

Paper 1 nghiên cứu vấn đề authorization evidence có thể đã cũ hoặc không còn phù hợp tại thời điểm tạo hiệu ứng bền vững. Vì vậy, bài đặt trọng tâm vào việc xác minh authorization tại ranh giới commit, thay vì chỉ dựa vào việc agent từng có quyền ở thời điểm trước đó.

Paper 2 tiếp cận vấn đề trong phạm vi hệ thống rộng hơn. Khi một root authority bị thu hồi, quyền cũ có thể vẫn được mang theo bởi các tiến trình đang chạy, tác vụ được ủy quyền, thông điệp đang chuyển giao hoặc các nghĩa vụ chưa hoàn tất. Do đó, bài không chỉ xem xét tính hợp lệ của một thao tác commit riêng lẻ mà còn quan tâm đến việc xác định và kiểm soát các đường có thể tiếp tục mang authority cũ đến những điểm tạo hiệu ứng.

FENCE cũng xuất phát từ vấn đề này. Một artifact được tạo từ dữ liệu hoặc trạng thái phụ thuộc vào authority ở epoch cũ có thể vẫn tồn tại sau khi revoke. Nếu agent tiếp tục sử dụng artifact đó để tạo một thao tác mới, chỉ kiểm tra xem agent còn giữ token cũ hay không có thể chưa đủ. FENCE vì thế đề xuất lưu lại support của artifact và kiểm tra support tại thời điểm commit, đồng thời đặt điều kiện fencing đối với các writer có liên quan trước khi xác nhận ACK.

**Mức độ trùng lặp:** Cao ở cấp độ vấn đề nghiên cứu. Cả ba hướng đều quan tâm đến việc ngăn hiệu ứng không còn đủ cơ sở authorization sau khi trạng thái authorization thay đổi. Khác biệt nằm ở phạm vi kiểm soát và cách xác định một thao tác còn được phép thực hiện hay không.

### 2.2. Cùng phải xử lý dependency giữa authorization và trạng thái được tạo ra

Paper 1 đã đề cập đến dependency giữa authorization evidence và trạng thái được suy ra. Vì vậy, ý tưởng duy trì mối liên hệ từ bằng chứng authorization đến trạng thái có thể tạo ra hiệu ứng bền vững không phải là điểm hoàn toàn mới của FENCE.

Paper 2 cũng xử lý mối quan hệ này, nhưng trong một mô hình rộng hơn, bao gồm root authority, support và các carrier hoặc nghĩa vụ có thể tiếp tục tồn tại trong quá trình thực thi bất đồng bộ.

FENCE biểu diễn dependency bằng các cặp `(authority, epoch)` được gắn vào artifact. Khi artifact được tạo từ các đầu vào khác, support được truyền sang artifact mới. Nếu một artifact vẫn phụ thuộc vào epoch đã bị thu hồi, CommitGateway có thể từ chối commit hoặc yêu cầu tái tạo artifact từ nguồn còn hợp lệ.

**Mức độ trùng lặp:** Cao về ý tưởng theo dõi dependency và ngăn dependency cũ tiếp tục dẫn đến hiệu ứng. Tuy nhiên, mức độ tương đương về mô hình dữ liệu, quy tắc lan truyền dependency và điều kiện vô hiệu hóa cần được đối chiếu chi tiết hơn.

### 2.3. Cùng đặt kiểm soát authorization ở ranh giới tạo hiệu ứng, thay vì chỉ kiểm tra lúc bắt đầu công việc

Paper 1 tập trung rõ vào việc làm mới và xác minh authorization evidence tại commit boundary. Bài cũng xem xét mối liên hệ giữa bằng chứng authorization và hiệu ứng dự định tạo ra. Vì vậy, một cơ chế chỉ kiểm tra quyền khi tác vụ bắt đầu sẽ chưa thể hiện đầy đủ vấn đề mà Paper 1 nghiên cứu.

Paper 2 xử lý vấn đề ở phạm vi hệ thống rộng hơn: cần kiểm soát các sink và đường thực thi có liên quan đến root authority đã bị thu hồi, thay vì chỉ dựa vào trạng thái của một agent hoặc một tiến trình.

FENCE cũng đặt kiểm tra tại CommitGateway. Trước khi chấp nhận một thao tác, gateway đối chiếu support của artifact với revocation frontier hiện hành. Nếu support chứa một epoch không còn hợp lệ, thao tác sẽ bị từ chối hoặc phải được tái tạo từ nguồn hợp lệ.

Tuy nhiên, có cùng đặt kiểm tra ở commit boundary không đồng nghĩa với việc ba cơ chế có cùng bảo đảm. Paper 1 kiểm tra nhiều điều kiện của authorization evidence; Paper 2 yêu cầu kiểm soát các đường có thể tiếp tục mang authority đến sink; còn FENCE nhấn mạnh quan hệ giữa support của artifact và frontier sau revoke.

**Mức độ trùng lặp:** Cao về nguyên tắc kiểm soát tại ranh giới tạo hiệu ứng, nhưng chưa thể kết luận các cơ chế tương đương nếu chưa so sánh đầy đủ các điều kiện và giả định của chúng.

**Ý nghĩa đối với FENCE:** Cần xác định liệu việc kết hợp support của artifact với frontier có giải quyết được trường hợp cụ thể nào mà các cơ chế trước không xử lý được hay không. Nếu các cơ chế trước có thể bảo đảm cùng kết quả khi được cung cấp đầy đủ dependency evidence và được triển khai đúng tại commit boundary, khác biệt của FENCE có thể chủ yếu nằm ở cách mô hình hóa hoặc triển khai.

### 2.4. Cùng phải cân bằng giữa thu hồi an toàn và giữ lại công việc còn hợp lệ

Thu hồi quyền có thể dẫn đến hai loại sai sót. Thứ nhất, hệ thống vẫn cho phép công việc phụ thuộc vào authority đã bị thu hồi tạo ra hiệu ứng. Thứ hai, hệ thống từ chối cả những công việc vẫn có thể được thực hiện hợp lệ nhờ một nguồn authorization độc lập.

Paper 2 đã nghiên cứu vấn đề support độc lập thông qua mô hình support có khả năng biểu diễn các lựa chọn thay thế, đồng thời xem xét việc rebind sang witness còn hợp lệ. Vì vậy, mục tiêu bảo toàn công việc độc lập không phải là một khoảng trống có thể mặc nhiên gán cho FENCE.

FENCE cũng hướng đến việc giữ lại công việc hợp lệ bằng cách cho phép re-derive artifact từ nguồn còn hợp lệ. Tuy nhiên, việc dùng một tập support đơn giản và cơ chế re-derive không tự động chứng minh rằng FENCE phân biệt chính xác giữa dependency bắt buộc và dependency có thể thay thế.

**Mức độ trùng lặp:** Cao ở cấp độ mục tiêu; mức độ tương đương về mô hình support và cách xác định nguồn authorization độc lập cần được xác minh thêm.

**Ý nghĩa đối với FENCE:** Cần chứng minh cách biểu diễn support của FENCE có ưu điểm cụ thể nào, hoặc xác định một lớp tình huống mà mô hình hiện tại chưa xử lý tốt. Nếu chưa chứng minh được điều đó, đây là vấn đề cần cải thiện trong thiết kế chứ chưa phải lợi thế của FENCE.

### 2.5. Cùng phải xử lý sự không đồng bộ giữa thời điểm revoke và thời điểm commit

Trong các hệ thống agent, thời điểm quyền bị thu hồi, thời điểm agent nhận được thông tin revoke và thời điểm thao tác thực sự được commit có thể khác nhau. Một tiến trình có thể tiếp tục sử dụng trạng thái cục bộ cũ; một thông điệp có thể đang trên đường chuyển giao; hoặc một thao tác có thể đã được khởi tạo nhưng chưa tạo ra hiệu ứng bền vững.

Paper 1 xem xét tính hợp lệ của authorization evidence tại thời điểm commit, trong khi Paper 2 mở rộng việc kiểm soát sang các tiến trình, carrier, đường chuyển giao và sink thuộc phạm vi root authority.

FENCE đặt ra thuộc tính PARS: sau khi revoke đã được ACK, không được commit thao tác được hỗ trợ bởi epoch đã bị thu hồi. Để bảo đảm thuộc tính này, FENCE đề xuất không chỉ cập nhật frontier mà còn fencing các writer liên quan trước khi xác nhận ACK, sau đó kiểm tra lại support tại commit.

Đây là điểm cần đặc biệt thận trọng khi xác định tính mới. Paper 2 đã nghiên cứu root cut và sink fencing, nên việc liên kết revoke với việc chặn các đường tạo hiệu ứng có thể đã có phần giao nhau đáng kể. Chưa thể kết luận rằng semantics ACK của FENCE là mới nếu chưa đối chiếu chính xác các điều kiện hoàn tất giao thức và phạm vi giả định.

**Mức độ trùng lặp:** Cao về mục tiêu bảo đảm không có hiệu ứng trái phép sau thời điểm revoke được xác nhận. Sự khác biệt tiềm năng nằm ở semantics của ACK, phạm vi các writer phải được fencing và cách chứng minh điều kiện an toàn đối với artifact hoặc branch đã tồn tại.

### 2.6. Nhận định tổng hợp về mức độ trùng lặp

Paper 1 tập trung vào commit-time authorization và tính hợp lệ của evidence; Paper 2 nghiên cứu root-scoped quiescence trong hệ thống agent bất đồng bộ; FENCE tập trung vào support của artifact, revocation frontier và điều kiện commit sau ACK.

## 3. Những khoảng trống cần xác minh

### 3.1. Hướng A — Nghiên cứu semantics của dependency ở cấp artifact

FENCE hiện mô hình hóa support dưới dạng tập các cặp `(authority, epoch)`. Khi artifact được tạo từ nhiều đầu vào, support của artifact được hợp thành từ support của các đầu vào.

Cách biểu diễn này cần được xem xét kỹ khi có nhiều nguồn authorization:

* Một artifact có bắt buộc phải dựa vào tất cả các nguồn đầu vào không?
* Hay chỉ cần một trong nhiều nguồn độc lập còn hợp lệ?
* Khi một nguồn bị thu hồi, hệ thống có thể xác định chính xác phần phụ thuộc cần loại bỏ và phần công việc vẫn có thể giữ lại không?
* Độ thô của support ảnh hưởng thế nào đến việc từ chối nhầm công việc vẫn hợp lệ?

Paper 2 đã có mô hình support biểu đạt được các trường hợp thay thế và kết hợp. Vì vậy, câu hỏi cần nghiên cứu không chỉ là làm thế nào truyền support, mà là liệu có thể xây dựng một mô hình phù hợp với artifact của agent, dễ kiểm chứng và có chi phí thấp hơn mà vẫn bảo đảm tính đúng đắn hay không.

**Điều cần xác minh:** Paper 1 và Paper 2 đã giải quyết đầy đủ bài toán support ở cấp artifact trong các tình huống mà FENCE quan tâm chưa? Nếu chưa, trường hợp cụ thể nào vẫn chưa được xử lý?

### 3.2. Hướng B — Semantics của ACK và việc fencing writer

FENCE đặt ra yêu cầu rằng ACK xác nhận revoke chỉ được phát ra sau khi các writer có khả năng tạo hiệu ứng dựa trên authority cũ đã được fencing hoặc đưa vào trạng thái an toàn theo giao thức.

Điểm cần phân biệt là ACK không chỉ thể hiện epoch đã tăng. Nó còn cần gắn với điều kiện ngăn các thao tác bị ảnh hưởng tiếp tục commit sau thời điểm xác nhận. Tuy nhiên, Paper 2 cũng có root cut, sink fencing và cơ chế xác minh trạng thái quiescence. Do đó, chưa thể mặc định rằng ràng buộc ACK của FENCE là mới.

**Điều cần xác minh:**

* Paper 2 đã bảo đảm điều kiện tương đương trong cùng phạm vi giả định chưa?
* Nếu có, FENCE có cung cấp một semantics khác hoặc một bảo đảm có thể chứng minh riêng không?
* Nếu khác biệt nằm ở mức đơn giản hóa triển khai, có thể đo lường được lợi ích về độ phức tạp, độ trễ hoặc chi phí vận hành không?

### 3.3. Hướng C — Xây dựng benchmark độc lập cho post-ACK revocation

FENCE dự kiến xây dựng bộ kiểm thử bao gồm các tình huống như stale branch, dependency bị mất khỏi metadata tường minh, cache cũ, tool queue trì hoãn, restart và race giữa revoke với commit. Tuy nhiên, sự tồn tại của một benchmark mới chưa đủ chứng minh tính mới. Paper 1 và Paper 2 đã có bộ kiểm thử và cơ chế kiểm tra riêng theo phạm vi của chúng.

**Điều cần xác minh:**

* Các benchmark hiện có đã bao phủ từng loại tình huống trên đến mức nào?
* Những kịch bản nào thực sự chưa được đánh giá?
* Benchmark của FENCE có thể tái hiện lịch thực thi và kiểm tra kết quả bằng một oracle độc lập hay chỉ đọc metadata của trace?
* Benchmark có kiểm tra đồng thời tính an toàn và lượng công việc hợp lệ được giữ lại không?

Cần chứng minh rằng các kịch bản mới đại diện cho một lớp lỗi hoặc điều kiện hệ thống chưa được đánh giá đầy đủ.
