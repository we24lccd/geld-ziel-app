// main.js

const goals = window.goalsFromServer || [];

function showGoalDetails(index) {
    document.querySelectorAll('.goal-item').forEach(el => el.classList.remove('active'));
    document.getElementById('goalItem' + index).classList.add('active');

    let goal = goals[index];
    let html = `
    <div class="goal-details position-relative">
        <form class="image-upload-form" style="position:absolute; top:10px; right:10px;">
            <input type="file" name="image" accept="image/*" style="display:none;" id="imageInput${index}" onchange="uploadImage(${index}, this.files[0])">
            <button type="button" class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('imageInput${index}').click()">🖼️ Cập nhật ảnh</button>
        </form>

        <div class="d-flex justify-content-between align-items-start mb-3">
            <div class="flex-grow-1 pr-3">
                <h3>${goal.description}</h3>
                <p><strong>Số tiền mục tiêu:</strong> ${goal.amount_fmt}</p>
                <p><strong>Hạn chót:</strong> ${goal.deadline || "Không có"}</p>
                <p><strong>Đã tích lũy:</strong> ${goal.total_saved_fmt}</p>
                <p><strong>Số tiền cần mỗi ngày:</strong> ${goal.daily_needed_fmt}</p>
                <div class="progress mb-2">
                    <div class="progress-bar" style="width: ${goal.progress_percent}%">
                        ${goal.progress_percent.toFixed(1)}%
                    </div>
                </div>
                ${goal.completed ? `<p class="text-success font-weight-bold">${goal.completion_message}</p>` : ""}
            </div>
            ${goal.image ? `
            <div style="max-width: 300px;">
                <img src="/static/images/${goal.image}" class="img-fluid rounded shadow-sm" style="width: 100%; border-radius: 12px;">
            </div>` : ""}
        </div>

        <h4 class="mt-3">📜 Quá Trình Tích Lũy</h4>
    <ul class="list-group">
        ${goal.deposits.map((d, i) => `
            <li class="list-group-item d-flex justify-content-between align-items-center flex-column flex-md-row">
                <div class="w-100">
                    <div>
                        <span class="font-weight-bold">${d.timestamp}:</span>
                        <span>${d.amount_fmt} VND (${d.percent}%)</span>
                    </div>
                    <div class="deposit-note-area mt-1">
                        ${
                            d.editingNote
                            ? `<input type="text" class="form-control form-control-sm d-inline-block" style="width:70%;max-width:250px;" 
                                    value="${d.note || ""}" 
                                    placeholder="Nhập ghi chú..." 
                                    onblur="saveDepositNote(${index}, ${i}, this.value)"
                                    onkeydown="if(event.key==='Enter'){saveDepositNote(${index}, ${i}, this.value)}">`
                            : d.note
                                ? `<span class="text-muted small">📝 ${d.note}</span>
                                <button class="btn btn-link btn-sm p-0 ml-2" style="font-size:1rem;" title="Sửa ghi chú" onclick="editDepositNote(${index}, ${i})">&#9998;</button>`
                                : `<button class="btn btn-link btn-sm p-0 text-secondary" onclick="editDepositNote(${index}, ${i})">+ Thêm ghi chú</button>`
                        }
                    </div>
                </div>
                <button class="delete-deposit-btn ml-md-2 mt-2 mt-md-0" onclick="deleteDeposit(${index}, ${i})">✖</button>
            </li>
        `).join('')}
    </ul>
        <div class="mt-3">
            <input type="number" id="depositInput${index}" class="form-control mb-2" placeholder="Nhập số tiền (VND)">
            <input type="text" id="depositNote${index}" class="form-control mb-2" placeholder="Ghi chú (tuỳ chọn)">
            <button class="btn btn-success btn-block" onclick="addDeposit(${index})">➕ Thêm Tích Lũy</button>
        </div>
    </div>`;
    document.getElementById('detailPanel').innerHTML = html;
}

function openAddGoalModal() {
    document.getElementById('addGoalModal').style.display = 'block';
}

function closeAddGoalModal() {
    document.getElementById('addGoalModal').style.display = 'none';
}

function addGoal() {
    let description = document.getElementById('goalDesc').value;
    let amount = parseFloat(document.getElementById('goalAmount').value);
    let deadline = document.getElementById('goalDeadline').value;

    if (!description || !amount || amount <= 0) {
        alert("Vui lòng nhập đầy đủ thông tin hợp lệ.");
        return;
    }

    fetch('/add_goal', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({description, amount, deadline})
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.reload();
    });
}

function deleteGoal(goalId) {
    if (!confirm("Bạn có chắc chắn muốn xoá mục tiêu này?")) return;
    fetch(`/goal/${goalId}`, {method: 'DELETE'})
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        document.getElementById('goalItem' + goalId).remove();
        document.getElementById('detailPanel').innerHTML = "<p>Chọn một mục tiêu để xem chi tiết.</p>";
    });
}

function addDeposit(goalId) {
    let amount = parseFloat(document.getElementById('depositInput' + goalId).value);
    let note = document.getElementById('depositNote' + goalId).value || "";
    if (!amount || amount <= 0) {
        alert("Vui lòng nhập số tiền hợp lệ.");
        return;
    }
    fetch(`/deposit/${goalId}`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({amount, note})
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        fetch(`/goal/${goalId}`)
        .then(res => res.json())
        .then(updatedGoal => {
            goals[goalId] = updatedGoal;
            showGoalDetails(goalId);
        });
    });
}

function deleteDeposit(goalId, depositId) {
    if (!confirm("Bạn có chắc chắn muốn xoá khoản tích lũy này?")) return;
    fetch(`/deposit/${goalId}/${depositId}`, {method: 'DELETE'})
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        fetch(`/goal/${goalId}`)
        .then(res => res.json())
        .then(updatedGoal => {
            goals[goalId] = updatedGoal;
            showGoalDetails(goalId);
        });
    });
}

function resetApp() {
    if (!confirm("Bạn có chắc chắn muốn xoá toàn bộ dữ liệu?")) return;
    fetch('/reset', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
        alert(data.message);
        location.reload();
    });
}

function editGoalDesc(goalId) {
    const titleEl = document.querySelector(`#goalItem${goalId} .goal-title`);
    const inputEl = document.getElementById(`editDesc${goalId}`);
    inputEl.value = titleEl.innerText;
    titleEl.classList.add('d-none');
    inputEl.classList.remove('d-none');
    inputEl.focus();
}

function saveGoalDesc(goalId) {
    const titleEl = document.querySelector(`#goalItem${goalId} .goal-title`);
    const inputEl = document.getElementById(`editDesc${goalId}`);
    const newDesc = inputEl.value.trim();

    if (!newDesc) {
        alert("Tên mục tiêu không được để trống.");
        return;
    }

    fetch(`/update_goal/${goalId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: newDesc })
    })
    .then(res => res.json())
    .then(data => {
        titleEl.innerText = newDesc;
        titleEl.classList.remove('d-none');
        inputEl.classList.add('d-none');
    });
}

function uploadImage(goalId, file) {
    if (!file) return;

    const formData = new FormData();
    formData.append("image", file);

    fetch(`/upload_image/${goalId}`, {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            fetch(`/goal/${goalId}`)
            .then(res => res.json())
            .then(updatedGoal => {
                goals[goalId] = updatedGoal;
                showGoalDetails(goalId);
            });
        } else {
            alert("Upload ảnh thất bại.");
        }
    })
    .catch(() => alert("Lỗi khi tải ảnh lên."));
}

function updateDepositNote(goalId, depositId, note) {
    fetch(`/deposit/${goalId}/${depositId}/note`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({note})
    })
    .then(res => res.json())
    .then(data => {
        // Cập nhật lại dữ liệu mục tiêu từ server để giữ đúng ghi chú mới nhất
        fetch(`/goal/${goalId}`)
        .then(res => res.json())
        .then(updatedGoal => {
            goals[goalId] = updatedGoal;
            showGoalDetails(goalId);
        });
    });
}

function editDepositNote(goalId, depositId) {
    goals[goalId].deposits[depositId].editingNote = true;
    showGoalDetails(goalId);
}

function saveDepositNote(goalId, depositId, note) {
    goals[goalId].deposits[depositId].editingNote = false;
    updateDepositNote(goalId, depositId, note);
}