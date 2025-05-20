from django import forms
from .models import Post
from django import forms
from django.contrib.auth import get_user_model
from .models import Department, GroupChat
from django import forms
from .models import Notification, Department, Task, User
from .models import Notification, Department, Task


from django import forms
from .models import Notification, Department, Task, User

User = get_user_model()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'avatar_url']
        labels = {
            'title': '',
            'avatar_url': 'Hình ảnh đính kèm',
        }
        widgets = {
            'title': forms.Textarea(attrs={
                'placeholder': 'Nhập nội dung bài viết',
                'class': 'form-control',
                'rows': 4
            }),
            'avatar_url': forms.URLInput(attrs={
                'placeholder': 'Nhập URL hình ảnh',
                'class': 'form-control'
            }),
        }


class EmployeeSearchForm(forms.Form):
    query = forms.CharField(
        required=False,
        label='Tìm kiếm',
        widget=forms.TextInput(attrs={'placeholder': 'Tìm theo tên...'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=False,
        label='Bộ phận',
        empty_label='Tất cả bộ phận'
    )

class CreateGroupForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Chọn thành viên'
    )

    class Meta:
        model = GroupChat
        fields = ['group_name', 'members']




class NotificationForm(forms.ModelForm):
    recipient_type = forms.ChoiceField(
        choices=[('all', 'Tất cả nhân viên'), ('department', 'Chọn bộ phận')],
        widget=forms.RadioSelect,
        label="Gửi đến"
    )

    class Meta:
        model = Notification
        fields = ['title', 'content', 'image', 'departments']
        widgets = {
            'departments': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'title': 'Tiêu đề',
            'content': 'Nội dung',
            'image': 'Ảnh đính kèm',
            'departments': 'Chọn bộ phận',
        }

    def clean(self):
        cleaned_data = super().clean()
        recipient_type = cleaned_data.get('recipient_type')
        departments = cleaned_data.get('departments')

        if recipient_type == 'department' and (not departments or len(departments) == 0):
            self.add_error('departments', 'Vui lòng chọn ít nhất một bộ phận khi gửi theo bộ phận.')

        return cleaned_data

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(queryset=User.objects.none(), label="Giao cho")

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Lấy user từ kwargs
        super(TaskForm, self).__init__(*args, **kwargs)

        if user:
            self.fields['assigned_to'].queryset = User.objects.filter(
                department_id=user.department_id
            ).exclude(id=user.id)
        else:
            self.fields['assigned_to'].queryset = User.objects.none()

    class Meta:
        model = Task
        fields = ['task_name', 'description', 'assigned_to', 'deadline']


class TaskAssignmentForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),  # Khởi tạo rỗng, sẽ fill trong __init__
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Lọc danh sách user cùng phòng ban và loại bỏ chính người giao việc
        if user and user.department:
            self.fields['users'].queryset = User.objects.filter(department=user.department).exclude(id=user.id)
        else:
            self.fields['users'].queryset = User.objects.none()

        # Ẩn trường status nếu có trong form (hoặc loại khỏi Meta.fields cũng được)
        if 'status' in self.fields:
            self.fields['status'].widget = forms.HiddenInput()

    class Meta:
        model = Task
        # KHÔNG đưa 'status' vào fields để tránh hiện trên giao diện
        fields = ['task_name', 'description', 'deadline']