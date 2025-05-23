import os
import uuid
from datetime import datetime

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model, authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import models
from .context_processors import get_unread_count
from .forms import PostForm, NotificationForm
from .models import Post, Comment, PrivateChat, PrivateMessage, Friend, GroupChat, GroupMember, Message, Notification, \
    UserNotification, TaskAssignment, Task
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max, F, OuterRef, Subquery, Count
from django.utils import timezone
import json
import logging
from .models import Department
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import TodoList
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from .models import Task
# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Like, Post


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('admin_home')
            else:
                return redirect('user_home')
    return render(request, 'mxh/login/login.html')

@login_required
def admin_home(request):
    return render(request, 'mxh/chat/chat_admin.html')

@login_required
def user_home(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('user_home')
    else:
        form = PostForm()
    comments = Comment.objects.all()
    posts = Post.objects.all().order_by('-created_at')
    chat = PrivateChat.objects.filter(Q(user1=request.user) | Q(user2=request.user)).first()
    context = {
        'form': form,
        'posts': posts,
        'comments': comments,
        'default_chat_id': chat.id if chat else None,
    }
    return render(request, 'mxh/home/home.html', context)

# Tạo bài viết
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('user_home')
    else:
        form = PostForm()
    return render(request, 'mxh/home/create_post.html', {'form': form})

# Bình luận
@login_required
def add_comment(request, post_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        post = get_object_or_404(Post, id=post_id)
        Comment.objects.create(post=post, user=request.user, content=content)
        if post.user != request.user:
            notif = Notification.objects.create(
                sender=request.user,
                title='Bình luận mới',
                content=f'{request.user.username} đã bình luận bài viết của bạn: "{content}"',
                type='personal',
                post = post
            )
            UserNotification.objects.create(notification=notif, user=post.user)
    return redirect('user_home')

# Danh sách bình luận
@login_required
def post_detail(request, post_id):
    post = Post.objects.get(id=post_id)
    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments,
    }
    return render(request, 'mxh/home/home.html', context)

# Tìm kiếm tên và bộ phận
User = get_user_model()
@login_required
def search_employees(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    users = User.objects.all()

    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    if department_id:
        users = users.filter(department_id=department_id)

    departments = Department.objects.all()

    context = {
        'users': users,
        'query': query,
        'department_id': department_id,
        'departments': departments,
    }
    return render(request, 'mxh/home/home.html', context)


# Đếm lượt thích
@login_required
def toggle_like(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')
        if not post_id:
            return HttpResponseBadRequest("Missing post_id")

        post = get_object_or_404(Post, id=post_id)
        user = request.user
        liked_obj, created = Like.objects.get_or_create(post=post, user=user)
        if not created:
            liked_obj.delete()
            liked_status = False
        else:
            liked_status = True

        if post.user != request.user:
            notif = Notification.objects.create(
                sender=request.user,
                title='Thích bài viết',
                content=f'{request.user.username} đã thích bài viết của bạn.',
                type='personal',
                post=post
            )
            UserNotification.objects.create(notification=notif, user=post.user)

        like_count = Like.objects.filter(post=post).count()
        return JsonResponse({'liked': liked_status, 'like_count': like_count})

    return HttpResponseBadRequest("Invalid request method")

@login_required
def start_chat(request, user_id):
    target_user = get_object_or_404(User, id=user_id)

    chat = PrivateChat.objects.filter(
        Q(user1=request.user, user2=target_user) | Q(user1=target_user, user2=request.user)
    ).first()

    if not chat:
        chat = PrivateChat.objects.create(user1=request.user, user2=target_user)

    return redirect('chat_room', chat_id=chat.id)



# Thêm tin nhắn cá nhân
@login_required
def add_message(request, chat_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        chat = get_object_or_404(PrivateChat, id=chat_id)
        PrivateMessage.objects.create(chat=chat, sender=request.user, content=content)
    return redirect('chat_room', chat_id=chat_id)

# Nhắn tin cá nhân
@login_required
def chat_room(request, chat_id):
    chat = get_object_or_404(PrivateChat, id=chat_id)
    messages = chat.privatemessage_set.all().order_by('sent_at')
    other_user = chat.get_receiver(request.user)

    chats = PrivateChat.objects.filter(Q(user1=request.user) | Q(user2=request.user))
    chat_list = [(c, c.user2 if c.user1 == request.user else c.user1) for c in chats]

    context = {
        'chat': chat,
        'messages': messages,
        'other_user': other_user,
        'chat_list.css': chat_list,
    }
    return render(request, 'mxh/chat/chat.html', context)


# Hiển thị danh sách tin nhắn
@login_required
def chat_view(request):
    chats = PrivateChat.objects.filter(Q(user1=request.user) | Q(user2=request.user))

    chat_list = []
    for c in chats:
        other = c.user2 if c.user1 == request.user else c.user1
        chat_list.append((c, other))

    context = {
        'chat_list': chat_list,
    }
    return render(request, 'mxh/chat/chat_list.html', context)

# Tạo nhóm chat
@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        member_ids = request.POST.getlist('members')

        group = GroupChat.objects.create(group_name=group_name, created_by=request.user)

        GroupMember.objects.create(group=group, user=request.user, role='admin')

        for member_id in member_ids:
            user = User.objects.get(id=member_id)
            GroupMember.objects.create(group=group, user=user, role='member')

        return redirect('group_chat_list')

    users = User.objects.exclude(id=request.user.id)
    return render(request, 'mxh/chat/create_chat.html', {'users': users})

# Nhắn tin trong group
@login_required
def group_chat_room(request, group_id):
    group = get_object_or_404(GroupChat, id=group_id)
    if not GroupMember.objects.filter(group=group, user=request.user).exists():
        return redirect('access_denied')  # hoặc render thông báo tùy bạn

    messages = Message.objects.filter(group=group).order_by('sent_at')
    members = GroupMember.objects.filter(group=group).select_related('user')

    context = {
        'group': group,
        'messages': messages,
        'members': members,
        'username': request.user.username,
    }
    return render(request, 'mxh/chat/group_chat_room.html', context)

# Thêm nhóm mới
@login_required
def add_group_message(request, group_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        group = get_object_or_404(GroupChat, id=group_id)
        Message.objects.create(group=group, sender=request.user, content=content)
    return redirect('group_chat_room', group_id=group_id)

#Hiển thị danh sách nhóm chat
@login_required
def group_chat_list(request):
    user_groups = GroupMember.objects.filter(user=request.user).select_related('group')
    group_chat_list = []
    for group_member in user_groups:
        group = group_member.group
        group_chat_list.append(group)

    context = {
        'group_chat_list': group_chat_list,
    }
    return render(request, 'mxh/chat/group_chat_list.html', context)

def is_admin(user):
    return user.is_staff or user.is_superuser

# Thông báo phía admin
@login_required
@user_passes_test(is_admin)
def admin_notifications(request):
    notifications = Notification.objects.filter(type='company').order_by('-created_at')
    return render(request, 'mxh/admin/notification_list.html', {
        'notifications': notifications
    })

# Tạo thông báo admin

@login_required
@user_passes_test(is_admin)
def admin_notification_create(request):
    departments = Department.objects.all()

    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.sender = request.user
            notification.type = 'company'
            recipient_type = form.cleaned_data['recipient_type']
            notification.is_global = (recipient_type == 'all')
            notification.code = "TB-" + datetime.now().strftime("%y%m%d%H%M%S")

            uploaded_image = request.FILES.get('image')
            if uploaded_image:
                notification.image = uploaded_image

            notification.save()

            departments_selected = form.cleaned_data['departments']
            if not notification.is_global:
                notification.departments.set(departments_selected)

            users = User.objects.all() if notification.is_global else User.objects.filter(department__in=departments_selected)

            UserNotification.objects.bulk_create([
                UserNotification(notification=notification, user=user, is_read=False)
                for user in users
            ])
            return redirect('admin_notifications')
    else:
        form = NotificationForm(initial={'recipient_type': 'all'})

    return render(request, 'mxh/admin/create_edit_notification.html', {
        'form': form,
        'departments': departments,
        'is_edit': False,
    })


@login_required
@user_passes_test(is_admin)
def admin_notification_edit(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    departments = Department.objects.all()

    if request.method == 'POST':
        form = NotificationForm(request.POST, request.FILES, instance=notification)

        if form.is_valid():
            updated_notification = form.save(commit=False)

            recipient_type = form.cleaned_data.get('recipient_type')
            updated_notification.is_global = (recipient_type == 'all')

            if request.POST.get('remove_image'):
                if notification.image:
                    notification.image.delete(save=False)
                updated_notification.image = None

            elif 'image' in request.FILES:
                updated_notification.image = request.FILES['image']

            updated_notification.save()

            if updated_notification.is_global:
                updated_notification.departments.clear()
            else:
                updated_notification.departments.set(form.cleaned_data['departments'])

            UserNotification.objects.filter(notification=notification).delete()

            if updated_notification.is_global:
                recipients = User.objects.filter(is_staff=False, is_superuser=False)
            else:
                recipients = User.objects.filter(
                    department__in=updated_notification.departments.all(),
                    is_staff=False,
                    is_superuser=False
                )

            UserNotification.objects.bulk_create([
                UserNotification(notification=updated_notification, user=user)
                for user in recipients
            ])
            return redirect('admin_notifications')

    else:
        initial = {
            'recipient_type': 'all' if notification.is_global else 'department',
        }
        form = NotificationForm(instance=notification, initial=initial)

    selected_departments = notification.departments.values_list('id', flat=True)

    return render(request, 'mxh/admin/create_edit_notification.html', {
        'form': form,
        'departments': departments,
        'notification': notification,
        'selected_departments': selected_departments,
        'is_edit': True,
    })



#Xóa thông báo admin
@login_required
@user_passes_test(is_admin)
def admin_notification_delete(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    if request.method == 'POST':
        if notification.image:
            notification.image.delete(save=False)
        UserNotification.objects.filter(notification=notification).delete()
        notification.delete()
    return redirect('admin_notifications')

@login_required
def notification_view(request):
    personal_notifications = Notification.objects.filter(usernotification__user=request.user, type='personal').order_by('-created_at')

    user_notifications = UserNotification.objects.filter(user=request.user,notification__in=personal_notifications)
    read_notifications = set(user_notifications.filter(is_read=True).values_list('notification_id', flat=True))

    for notification in personal_notifications:
        notification.is_read = notification.id in read_notifications

    personal_unread_count = get_unread_count(request.user, 'personal')

    company_unread_count = get_unread_count(request.user, 'company')

    return render(request, 'mxh/notification/notification_personal.html', {
        'personal_notifications': personal_notifications,
        'personal_unread_count': personal_unread_count,
        'company_unread_count': company_unread_count
    })

@login_required
def notification_company(request):
    user_departments = request.user.department

    company_notifications = (Notification.objects.filter(type='company')
                             .filter(Q(is_global=True) | Q(departments=user_departments))
                             .order_by('-created_at'))

    user_notifications = UserNotification.objects.filter(user=request.user, notification__in=company_notifications
    )
    read_notifications = set(user_notifications.filter(is_read=True).values_list('notification_id', flat=True))

    for notification in company_notifications:
        notification.is_read = notification.id in read_notifications

    company_unread_count = get_unread_count(request.user, 'company')

    personal_unread_count = get_unread_count(request.user, 'personal')

    return render(request, 'mxh/notification/notification_company.html', {
        'company_notifications': company_notifications,
        'company_unread_count': company_unread_count,
        'personal_unread_count': personal_unread_count,
    })

@login_required
def notification_company_detail(request, pk):
    notification = get_object_or_404(Notification, pk=pk, type='company')

    user_notification = UserNotification.objects.get(user=request.user, notification=notification)
    if not user_notification.is_read:
        user_notification.is_read = True
        user_notification.save()

    personal_unread_count = get_unread_count(request.user, 'personal')
    company_unread_count = get_unread_count(request.user, 'company')

    return render(request, 'mxh/notification/company_notification_detail.html', {
        'notification': notification,
        'personal_unread_count': personal_unread_count,
        'company_unread_count': company_unread_count,
    })

@login_required
def profile(request, username):
    profile_user = User.objects.get(username=username)
    user_posts = Post.objects.filter(user=profile_user).order_by('-created_at')
    post_count = user_posts.count()
    post_id = request.GET.get('post_id')

    return render(request, 'mxh/profile/profile.html', {
        'profile_user': profile_user,
        'user_posts': user_posts,
        'post_count': post_count,
        'post_id': post_id,
    })


from django.urls import reverse
from django.shortcuts import redirect

def redirect_notification(request, notification_id):
    user_notification = get_object_or_404(
        UserNotification,
        notification_id=notification_id,
        user=request.user
    )

    user_notification.is_read = True
    user_notification.save()

    notification = user_notification.notification
    if notification.post:
        username = notification.post.user.username
        post_id = notification.post.id
        return redirect(f"/profile/{username}/#post-{post_id}")

    return redirect('notification_view')

@login_required
def update_avatar(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        user = request.user
        user.avatar_url = request.FILES['avatar']
        user.save()
    return redirect(reverse('user_profile', kwargs={'username': request.user.username}))

class TaskForm:
    pass

# Công việc
@login_required
def task_view(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.status = 'pending'
            task.save()

            assigned_user = form.cleaned_data['assigned_to']
            TaskAssignment.objects.create(task=task, user=assigned_user)
            TaskAssignment.objects.create(task=task, user=request.user)

            messages.success(request, f"Đã giao công việc cho {assigned_user.get_full_name() or assigned_user.username}")
            return redirect('task_view')
        else:
            messages.error(request, "Form không hợp lệ, hãy kiểm tra lại.")
    else:
        form = TaskForm(user=request.user)

    department_users = User.objects.filter(department_id=request.user.department_id).exclude(id=request.user.id).exclude(department_id__isnull=True)
    assigned_by_me = Task.objects.filter(assigned_by=request.user)
    assigned_to_me = [a.task for a in TaskAssignment.objects.filter(user=request.user)]

    return render(request, 'mxh/Task/task.html', {
        'form': form,
        'assigned_by_me': assigned_by_me,
        'assigned_to_me': assigned_to_me,
        'department_users': department_users,
    })




from .forms import TaskAssignmentForm
from .models import Task, TaskAssignment
@login_required
def create_task_view(request):
    if request.method == 'POST':
        form = TaskAssignmentForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.status = 'pending'  # Gán mặc định
            task.save()

            for user in form.cleaned_data['users']:
                TaskAssignment.objects.create(task=task, user=user)

            return redirect('task_view')
    else:
        form = TaskAssignmentForm(user=request.user)

    return render(request, 'mxh/task/taskform.html', {'form': form})

@login_required
def task_list_view(request):
    tasks_assigned_by_me = Task.objects.filter(assigned_by=request.user)
    assignments = TaskAssignment.objects.filter(user=request.user).select_related('task')

    pending_tasks = set(a.task for a in assignments if a.task.status == 'pending') | \
                    set(task for task in tasks_assigned_by_me if task.status == 'pending')

    completed_tasks = set(a.task for a in assignments if a.task.status == 'completed') | \
                      set(task for task in tasks_assigned_by_me if task.status == 'completed')
    for task in pending_tasks:
        task.assigned_to = [assignment.user for assignment in TaskAssignment.objects.filter(task=task)]

    for task in completed_tasks:
        task.assigned_to = [assignment.user for assignment in TaskAssignment.objects.filter(task=task)]

    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'assignments': assignments,  # Truyền assignments vào context
    }
    return render(request, 'mxh/task/task.html', context)

@login_required
def task_list(request):
    pending_tasks = Task.objects.filter(status='pending')
    completed_tasks = Task.objects.filter(status='completed')
    return render(request, 'task_list.html', {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks
    })

@login_required
def change_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if task.assigned_by == request.user or \
       task.taskassignment_set.filter(user=request.user).exists():
        if request.method == 'POST':
            if 'status' in request.POST:
                task.status = 'completed'
            else:
                task.status = 'pending'
            task.save()

    return redirect('task_view')

@login_required
def create_todo(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        if task_name:
            TodoList.objects.create(
                user=request.user,
                task_name=task_name,
                status='pending'
            )
        return redirect('todo_list')

    return render(request, 'mxh/task/todo_list.html')

@login_required
def todo_list(request):
    if request.method == 'POST':
        task_name = request.POST.get('task_name')
        if task_name:
            TodoList.objects.create(user=request.user, task_name=task_name)
        return redirect('todo_list')

    tasks = TodoList.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'mxh/task/todo_list.html', {'tasks': tasks})

@login_required
def toggle_status(request, task_id):
    task = get_object_or_404(TodoList, id=task_id, user=request.user)
    task.status = 'completed' if task.status == 'pending' else 'pending'
    task.save()
    return redirect('todo_list')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(TodoList, id=task_id, user=request.user)
    task.delete()
    return redirect('todo_list')


@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        new_image = request.FILES.get('new_image')
        remove_image = request.POST.get('remove_image')

        post.title = title

        if remove_image == 'true':
            post.avatar_url.delete(save=False)
            post.avatar_url = None
        elif new_image:
            post.avatar_url = new_image

        post.save()
        return redirect('user_profile', username=request.user.username)




@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    post.delete()

    return redirect('user_profile', username=request.user.username)
