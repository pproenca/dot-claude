# Django Styleguide Reference

## Core Philosophy

**Business logic should live in:**

- **Services** - Functions that write to the database
- **Selectors** - Functions that read from the database
- Model properties (simple derived values only)
- Model `clean` method (simple validations only)

**Business logic should NOT live in:**

- APIs and Views
- Serializers and Forms
- Model `save` method
- Custom managers or querysets
- Signals

## Service Layer

### Function-Based Service

```python
def user_create(
    *,
    email: str,
    name: str
) -> User:
    user = User(email=email)
    user.full_clean()
    user.save()

    profile_create(user=user, name=name)
    confirmation_email_send(user=user)

    return user
```

Key patterns:

- Keyword-only arguments (`*,`)
- Type annotations
- Call `full_clean()` before `save()`
- Compose with other services

### Class-Based Service

Use for namespacing related operations or multi-step flows:

```python
class FileDirectUploadService:
    def __init__(self, user: BaseUser):
        self.user = user

    @transaction.atomic
    def start(self, *, file_name: str, file_type: str) -> Dict[str, Any]:
        file = File(
            original_file_name=file_name,
            file_name=file_generate_name(file_name),
            file_type=file_type,
            uploaded_by=self.user,
        )
        file.full_clean()
        file.save()
        return {"id": file.id, "upload_url": generate_presigned_url(file)}

    @transaction.atomic
    def finish(self, *, file: File) -> File:
        file.upload_finished_at = timezone.now()
        file.full_clean()
        file.save()
        return file
```

### Naming Convention

Pattern: `<entity>_<action>`

- `user_create`, `user_update`, `user_deactivate`
- `order_place`, `order_cancel`, `order_refund`

Benefits: Easy to grep, natural namespace in `services.py`.

## Selectors

Selectors handle data fetching:

```python
def user_list(*, fetched_by: User) -> Iterable[User]:
    user_ids = user_get_visible_for(user=fetched_by)
    return User.objects.filter(id__in=user_ids)

def user_get(*, user_id: int) -> User:
    return get_object_or_404(User, id=user_id)
```

Use `django-filter` for complex filtering:

```python
import django_filters

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ('id', 'email', 'is_admin')

def user_list(*, filters=None):
    filters = filters or {}
    qs = User.objects.all()
    return UserFilter(filters, qs).qs
```

## Model Patterns

### Base Model

```python
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### Validation with Constraints

```python
class Course(BaseModel):
    name = models.CharField(unique=True, max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="start_date_before_end_date",
                check=Q(start_date__lt=F("end_date"))
            )
        ]

    def clean(self):
        if self.start_date >= self.end_date:
            raise ValidationError("End date cannot be before start date")
```

### Properties vs Selectors

Use properties for:

- Simple derived values from non-relational fields

```python
@property
def has_started(self) -> bool:
    return self.start_date <= timezone.now().date()
```

Use selectors when:

- Spanning multiple relations
- Complex calculations
- Could cause N+1 queries

## API Patterns (DRF)

### API Structure

```python
class UserCreateApi(APIView):
    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        name = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(**serializer.validated_data)

        return Response(
            self.OutputSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
```

Key patterns:

- Nested `InputSerializer` and `OutputSerializer`
- Never put business logic in API
- Inherit from plain `APIView`, not generic views

### Inline Serializers

```python
class OrderDetailApi(APIView):
    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        items = inline_serializer(many=True, fields={
            'id': serializers.IntegerField(),
            'product_name': serializers.CharField(),
            'quantity': serializers.IntegerField(),
        })
```

### Pagination

```python
from styleguide_example.api.pagination import get_paginated_response, LimitOffsetPagination

class UserListApi(APIView):
    class Pagination(LimitOffsetPagination):
        default_limit = 25

    class FilterSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        is_admin = serializers.NullBooleanField(required=False)

    class OutputSerializer(serializers.Serializer):
        id = serializers.IntegerField()
        email = serializers.EmailField()

    def get(self, request):
        filters_serializer = self.FilterSerializer(data=request.query_params)
        filters_serializer.is_valid(raise_exception=True)

        users = user_list(filters=filters_serializer.validated_data)

        return get_paginated_response(
            pagination_class=self.Pagination,
            serializer_class=self.OutputSerializer,
            queryset=users,
            request=request,
            view=self
        )
```

## Exception Handling

### Custom Exception Handler

```python
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.views import exception_handler
from rest_framework import exceptions
from rest_framework.serializers import as_serializer_error

def custom_exception_handler(exc, ctx):
    if isinstance(exc, DjangoValidationError):
        exc = exceptions.ValidationError(as_serializer_error(exc))

    if isinstance(exc, Http404):
        exc = exceptions.NotFound()

    if isinstance(exc, PermissionDenied):
        exc = exceptions.PermissionDenied()

    response = exception_handler(exc, ctx)

    if response is None:
        return response

    # Normalize to consistent structure
    if isinstance(exc.detail, (list, dict)):
        response.data = {"detail": response.data}

    return response
```

### Application-Specific Errors

```python
# core/exceptions.py
class ApplicationError(Exception):
    def __init__(self, message: str, extra: dict = None):
        self.message = message
        self.extra = extra or {}

# Usage in services
def order_place(*, user: User, items: list) -> Order:
    if not items:
        raise ApplicationError(
            message="Cannot place empty order",
            extra={"code": "EMPTY_ORDER"}
        )
```

## Celery Integration

### Task as Interface

```python
# tasks.py
from celery import shared_task

@shared_task
def email_send(email_id: int):
    email = Email.objects.get(id=email_id)

    from styleguide_example.emails.services import email_send
    email_send(email)

# services.py (calling the task)
from styleguide_example.emails.tasks import email_send as email_send_task

@transaction.atomic
def user_complete_onboarding(user: User) -> User:
    email = email_get_onboarding_template(user=user)

    # Call task after transaction commits
    transaction.on_commit(lambda: email_send_task.delay(email.id))

    return user
```

Key patterns:

- Import service inside task function (prevents circular imports)
- Import task with `_task` suffix
- Use `transaction.on_commit` for task dispatch

### Error Handling in Tasks

```python
@shared_task(bind=True, on_failure=_email_send_failure)
def email_send(self, email_id: int):
    email = Email.objects.get(id=email_id)

    from styleguide_example.emails.services import email_send

    try:
        email_send(email)
    except Exception as exc:
        logger.warning(f"Email send failed: {exc}")
        self.retry(exc=exc, countdown=5)
```

## Testing Patterns

### Service Tests

```python
class UserCreateTests(TestCase):
    def test_user_create_sends_confirmation_email(self):
        with patch('project.users.services.confirmation_email_send') as mock:
            user = user_create(email="test@example.com", name="Test")

            mock.assert_called_once_with(user=user)

    def test_user_create_validates_email_uniqueness(self):
        user_create(email="existing@example.com", name="First")

        with self.assertRaises(ValidationError):
            user_create(email="existing@example.com", name="Second")
```

### Factories with factory_boy

```python
import factory
from factory.django import DjangoModelFactory

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    name = factory.Faker("name")

# Usage
user = UserFactory()
admin = UserFactory(is_admin=True)
```

## URL Patterns

```python
from django.urls import path, include

user_patterns = [
    path('', UserListApi.as_view(), name='list'),
    path('<int:user_id>/', UserDetailApi.as_view(), name='detail'),
    path('create/', UserCreateApi.as_view(), name='create'),
    path('<int:user_id>/update/', UserUpdateApi.as_view(), name='update'),
]

urlpatterns = [
    path('users/', include((user_patterns, 'users'))),
]
```

## Settings Structure

```
config/
├── django/
│   ├── base.py          # All settings, imports from config/settings/
│   ├── local.py         # Local dev overrides
│   ├── production.py    # Production overrides
│   └── test.py          # Test overrides
├── settings/
│   ├── celery.py        # Celery config
│   ├── cors.py          # CORS config
│   └── sentry.py        # Error tracking
├── env.py               # Environment reading
└── urls.py
```

Integration pattern:

```python
# config/settings/sentry.py
from config.env import env

SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    sentry_sdk.init(dsn=SENTRY_DSN)
```

## Generic Update Service

```python
def model_update(
    *,
    instance: Model,
    fields: list[str],
    data: dict,
) -> tuple[Model, bool]:
    has_updated = False

    for field in fields:
        if field in data:
            if getattr(instance, field) != data[field]:
                setattr(instance, field, data[field])
                has_updated = True

    if has_updated:
        instance.full_clean()
        instance.save(update_fields=fields)

    return instance, has_updated

# Usage
def user_update(*, user: User, data: dict) -> User:
    user, _ = model_update(
        instance=user,
        fields=['first_name', 'last_name'],
        data=data
    )
    return user
```
