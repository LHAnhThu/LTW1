document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements - Tabs
    const phanViecTab = document.getElementById('phanViecTab');
    const todoListTab = document.getElementById('todoListTab');
    const phanViecContent = document.getElementById('phanViecContent');
    const todoListContent = document.getElementById('todoListContent');

    // DOM Elements - Phân việc
    const notCompletedList = document.getElementById('notCompletedList');
    const completedList = document.getElementById('completedList');
    const notCompletedCount = document.getElementById('notCompletedCount');
    const completedCount = document.getElementById('completedCount');
    const notCompletedHeader = document.getElementById('notCompletedHeader');
    const completedHeader = document.getElementById('completedHeader');
    const assignTaskBtn = document.getElementById('assignTaskBtn');
    const taskModal = document.getElementById('taskModal');
    const cancelBtn = document.getElementById('cancelBtn');
    const taskForm = document.getElementById('taskForm');
    const taskImage = document.getElementById('taskImage');
    const imagePreview = document.getElementById('imagePreview');

    // DOM Elements - To do list
    const todoInput = document.getElementById('todoInput');
    const addTodoBtn = document.getElementById('addTodoBtn');
    const todoList = document.getElementById('todoList');
    const deleteTodoModal = document.getElementById('deleteTodoModal');
    const deleteTodoName = document.getElementById('deleteTodoName');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');

    // Sample data for tasks
    const tasks = [
        {
            id: 1,
            title: 'Cất bớt gà vào kho',
            assignee: 'Xuân',
            avatar: 'https://via.placeholder.com/30',
            status: 'pending',
            date: '26/03',
            completed: false,
            image: null
        },
        {
            id: 2,
            title: 'Kiểm tra hạn sử dụng của hàng hóa trong kho',
            assignee: 'Minh',
            avatar: 'https://via.placeholder.com/30',
            status: 'accepted',
            date: '26/03',
            completed: false,
            image: null
        },
        {
            id: 3,
            title: 'Kiểm tra hàng tồn gà còn bao nhiêu',
            assignee: 'Xuân',
            avatar: 'https://via.placeholder.com/30',
            status: 'completed',
            date: '25/03',
            completed: true,
            image: null
        },
        {
            id: 4,
            title: 'Vệ sinh kho hàng',
            assignee: 'Minh',
            avatar: 'https://via.placeholder.com/30',
            status: 'completed',
            date: '24/03',
            completed: true,
            image: null
        }
    ];

    // Sample data for todo list
    let todos = [
        { id: 1, text: 'Chuẩn bị hàng sẵn', completed: false },
        { id: 2, text: 'Kiểm tra nguyên liệu', completed: false },
        { id: 3, text: 'Xếp hàng trong kho', completed: false },
        { id: 4, text: 'Giặt đồng phục', completed: true },
        { id: 5, text: 'Dọn khu vực bếp', completed: true }
    ];

    // Current todo being deleted
    let currentDeleteTodoId = null;

    // Initialize the application
    function init() {
        initializeTasks();
        initializeTodos();
        setupEventListeners();
    }

    // Setup Event Listeners
    function setupEventListeners() {
        // Tab navigation
        phanViecTab.addEventListener('click', () => switchTab('phan-viec'));
        todoListTab.addEventListener('click', () => switchTab('todo-list'));

        // Phân việc
        notCompletedHeader.addEventListener('click', () => switchTaskList('not-completed'));
        completedHeader.addEventListener('click', () => switchTaskList('completed'));
        assignTaskBtn.addEventListener('click', showTaskModal);
        cancelBtn.addEventListener('click', hideTaskModal);
        taskForm.addEventListener('submit', addNewTask);
        taskImage.addEventListener('change', previewImage);

        // To do list
        addTodoBtn.addEventListener('click', addTodo);
        todoInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                addTodo();
            }
        });
        cancelDeleteBtn.addEventListener('click', hideDeleteTodoModal);
        confirmDeleteBtn.addEventListener('click', confirmDeleteTodo);

        // Close modals when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target === taskModal) {
                hideTaskModal();
            }
            if (event.target === deleteTodoModal) {
                hideDeleteTodoModal();
            }
        });
    }

    // Switch between tabs
    function switchTab(tabName) {
        if (tabName === 'phan-viec') {
            phanViecTab.classList.add('active');
            todoListTab.classList.remove('active');
            phanViecContent.classList.add('active');
            todoListContent.classList.remove('active');
        } else {
            phanViecTab.classList.remove('active');
            todoListTab.classList.add('active');
            phanViecContent.classList.remove('active');
            todoListContent.classList.add('active');
        }
    }

    // ===== PHÂN VIỆC FUNCTIONALITY =====

    // Initialize the task lists
    function initializeTasks() {
        // Clear task containers
        notCompletedList.innerHTML = '';
        completedList.innerHTML = '';

        // Filter tasks by completion status
        const notCompletedTasks = tasks.filter(task => !task.completed);
        const completedTasks = tasks.filter(task => task.completed);

        // Update counters
        notCompletedCount.textContent = notCompletedTasks.length;
        completedCount.textContent = completedTasks.length;

        // Render not completed tasks
        notCompletedTasks.forEach(task => {
            notCompletedList.appendChild(createTaskElement(task));
        });

        // Render completed tasks
        completedTasks.forEach(task => {
            completedList.appendChild(createTaskElement(task));
        });
    }

    // Create a task element
    function createTaskElement(task) {
        const taskEl = document.createElement('div');
        taskEl.className = 'task-item';
        taskEl.dataset.id = task.id;

        let taskHTML = `
            <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''}>
            <div class="task-info">
                <div class="task-assignee">
                    <img src="${task.avatar}" alt="${task.assignee}" class="assignee-avatar">
                    <span class="assignee-name">${task.assignee}</span>
                </div>
                <div class="task-title">${task.title}</div>
        `;

        // Add image if exists
        if (task.image) {
            taskHTML += `<img src="${task.image}" alt="Task Image" class="task-image">`;
        }

        taskHTML += `
            </div>
            <div class="task-date">${task.date}</div>
        `;

        taskEl.innerHTML = taskHTML;

        // Add event listener to checkbox
        const checkbox = taskEl.querySelector('.task-checkbox');
        checkbox.addEventListener('change', () => {
            toggleTaskCompletion(task.id);
        });

        return taskEl;
    }

    // Toggle task completion status
    function toggleTaskCompletion(taskId) {
        const taskIndex = tasks.findIndex(task => task.id === taskId);
        if (taskIndex !== -1) {
            tasks[taskIndex].completed = !tasks[taskIndex].completed;

            // If task is marked as completed, update its status
            if (tasks[taskIndex].completed) {
                tasks[taskIndex].status = 'completed';
            } else {
                // If task is unmarked, revert to accepted status
                tasks[taskIndex].status = 'accepted';
            }

            // Re-initialize tasks to update the UI
            initializeTasks();
        }
    }

    // Switch between task lists
    function switchTaskList(listType) {
        if (listType === 'not-completed') {
            notCompletedList.classList.add('active');
            completedList.classList.remove('active');
            notCompletedHeader.classList.add('active');
            completedHeader.classList.remove('active');
        } else {
            notCompletedList.classList.remove('active');
            completedList.classList.add('active');
            notCompletedHeader.classList.remove('active');
            completedHeader.classList.add('active');
        }
    }

    // Show task assignment modal
    function showTaskModal() {
        taskModal.style.display = 'flex';
    }

    // Hide task assignment modal
    function hideTaskModal() {
        taskModal.style.display = 'none';
        taskForm.reset();
        imagePreview.innerHTML = '';
    }

    // Preview uploaded image
    function previewImage(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
            };
            reader.readAsDataURL(file);
        }
    }

    // Add a new task
    function addNewTask(event) {
        event.preventDefault();

        const title = document.getElementById('taskTitle').value;
        const assignTo = document.getElementById('assignTo').value;
        const deadline = document.getElementById('deadline').value;
        const file = taskImage.files[0];

        if (!title || !assignTo) {
            alert('Vui lòng nhập tiêu đề và chọn người được giao việc!');
            return;
        }

        // Format date (assuming deadline is in YYYY-MM-DD format)
        const dateObj = deadline ? new Date(deadline) : new Date();
        const formattedDate = `${dateObj.getDate()}/${dateObj.getMonth() + 1}`;

        // Create new task
        const newTask = {
            id: tasks.length + 1,
            title: title,
            assignee: assignTo,
            avatar: 'https://via.placeholder.com/30',
            status: 'pending',
            date: formattedDate,
            completed: false,
            image: null
        };

        // Handle image if uploaded
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                newTask.image = e.target.result;
                tasks.push(newTask);
                initializeTasks();
            };
            reader.readAsDataURL(file);
        } else {
            // Add to tasks array without image
            tasks.push(newTask);
            // Update UI
            initializeTasks();
        }

        // Hide modal
        hideTaskModal();
    }

    // ===== TO DO LIST FUNCTIONALITY =====

    // Initialize the todo list
    function initializeTodos() {
        todoList.innerHTML = '';

        todos.forEach(todo => {
            todoList.appendChild(createTodoElement(todo));
        });
    }

    // Create a todo element
    function createTodoElement(todo) {
        const todoEl = document.createElement('div');
        todoEl.className = `todo-item ${todo.completed ? 'completed' : ''}`;
        todoEl.dataset.id = todo.id;

        todoEl.innerHTML = `
            <input type="checkbox" class="todo-checkbox" ${todo.completed ? 'checked' : ''}>
            <span class="todo-text">${todo.text}</span>
            <span class="todo-delete"><i class="fas fa-trash"></i></span>
        `;

        // Add event listener to checkbox
        const checkbox = todoEl.querySelector('.todo-checkbox');
        checkbox.addEventListener('change', () => {
            toggleTodoCompletion(todo.id);
        });

        // Add event listener to delete button
        const deleteBtn = todoEl.querySelector('.todo-delete');
        deleteBtn.addEventListener('click', () => {
            showDeleteTodoModal(todo.id, todo.text);
        });

        return todoEl;
    }

    // Add a new todo
    function addTodo() {
        const text = todoInput.value.trim();

        if (text) {
            const newTodo = {
                id: todos.length > 0 ? Math.max(...todos.map(t => t.id)) + 1 : 1,
                text: text,
                completed: false
            };

            todos.push(newTodo);
            todoList.appendChild(createTodoElement(newTodo));
            todoInput.value = '';
        }
    }

    // Toggle todo completion status
    function toggleTodoCompletion(todoId) {
        const todoIndex = todos.findIndex(todo => todo.id === todoId);
        if (todoIndex !== -1) {
            todos[todoIndex].completed = !todos[todoIndex].completed;
            initializeTodos();
        }
    }

    // Show delete todo confirmation modal
    function showDeleteTodoModal(todoId, todoText) {
        currentDeleteTodoId = todoId;
        deleteTodoName.textContent = todoText;
        deleteTodoModal.style.display = 'flex';
    }

    // Hide delete todo confirmation modal
    function hideDeleteTodoModal() {
        deleteTodoModal.style.display = 'none';
        currentDeleteTodoId = null;
    }

    // Confirm delete todo
    function confirmDeleteTodo() {
        if (currentDeleteTodoId) {
            todos = todos.filter(todo => todo.id !== currentDeleteTodoId);
            initializeTodos();
            hideDeleteTodoModal();
        }
    }

    // Initialize the application
    init();
});
function switchTab(tabId) {
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.task-tab-content').forEach(tab => tab.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById(tabId).classList.add('active');
}


function showTab(tabName) {
    document.getElementById("pending-tasks").style.display = (tabName === 'pending') ? "block" : "none";
    document.getElementById("completed-tasks").style.display = (tabName === 'completed') ? "block" : "none";

    let tabs = document.querySelectorAll(".tab");
    tabs.forEach(tab => tab.classList.remove("active"));

    if (tabName === 'pending') {
        tabs[0].classList.add("active");
    } else {
        tabs[1].classList.add("active");
    }
}

// Gọi mặc định khi trang load
window.onload = function() {
    showTab('pending');
}
