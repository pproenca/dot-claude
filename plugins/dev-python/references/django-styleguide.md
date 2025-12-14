# Django Style Guide

Best practices for Django projects following the services/selectors pattern.

## Project Structure

```
config/
├── django/
│   ├── base.py           # Shared settings
│   ├── local.py          # Development settings
│   ├── production.py     # Production settings
│   └── test.py           # Test settings
├── urls.py
├── wsgi.py
└── asgi.py

apps/
├── core/
│   ├── models.py         # BaseModel with timestamps
│   ├── exceptions.py     # ApplicationError
│   └── pagination.py     # Standard pagination
├── users/
│   ├── models.py
│   ├── services.py       # Write operations
│   ├── selectors.py      # Read operations
│   ├── apis.py           # API endpoints
│   └── tests/
│       ├── test_services.py
│       ├── test_selectors.py
│       └── test_apis.py
└── ingredients/
    ├── models.py
    ├── services.py
    ├── selectors.py
    ├── apis.py
    └── tests/
```

## Service Layer Pattern

### Philosophy

**Business logic lives in services, not views.**

Benefits:
- Testable without HTTP layer
- Reusable across views, management commands, Celery tasks
- Clear separation of concerns

### Service Functions

```python
# services.py
from django.db import transaction

@transaction.atomic
def user_create(*, email: str, name: str, password: str) -> User:
    """
    Create a new user with validated data.

    Raises:
        ValidationError: If email already exists
    """
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already registered")

    user = User.objects.create(
        email=email,
        name=name,
    )
    user.set_password(password)
    user.save()

    # Side effects via explicit calls, not signals
    send_welcome_email.delay(user.id)

    return user
```

### Service Conventions

1. **Use keyword-only arguments** (`*` in signature)
2. **Return domain objects**, not serialized data
3. **Raise domain exceptions**, let views handle HTTP
4. **Use `@transaction.atomic`** for write operations
5. **Explicit side effects**, avoid Django signals

## Selector Pattern

### Selector Functions

```python
# selectors.py
from django.db.models import QuerySet

def user_list(*, filters: dict | None = None) -> QuerySet[User]:
    """
    Return filtered user queryset.

    Filters:
        - email: Exact email match
        - is_active: Boolean filter
    """
    qs = User.objects.all()

    if filters is None:
        return qs

    return UserFilter(filters, queryset=qs).qs

def user_get(*, user_id: int) -> User:
    """
    Get user by ID.

    Raises:
        User.DoesNotExist: If user not found
    """
    return User.objects.get(id=user_id)
```

### Selector Conventions

1. **Return QuerySets** for lists (allows further filtering)
2. **Return model instances** for single objects
3. **Use django-filter** for complex filtering
4. **Include related objects** with select_related/prefetch_related

## API Layer

### View Structure

```python
# apis.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserCreateApi(APIView):
    """Create a new user."""

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        name = serializers.CharField(max_length=100)
        password = serializers.CharField(min_length=8, write_only=True)

    class OutputSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ['id', 'email', 'name', 'created_at']

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = user_create(**serializer.validated_data)

        return Response(
            self.OutputSerializer(user).data,
            status=status.HTTP_201_CREATED
        )
```

### API Conventions

1. **Nested serializers** - InputSerializer and OutputSerializer inside view
2. **Thin views** - Delegate to services/selectors
3. **Explicit status codes** - Use status module constants
4. **Keyword unpacking** - Pass validated_data to services

## Model Layer

### Base Model

```python
# core/models.py
from django.db import models

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
```

### Model Conventions

```python
# users/models.py
from core.models import BaseModel

class User(BaseModel):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.email
```

1. **Inherit from BaseModel** for timestamps
2. **No business logic in models** - Use services
3. **No `save()` overrides** - Use services
4. **Minimal model methods** - Only for data representation

## ORM Best Practices

### Avoiding N+1 Queries

```python
# BAD - N+1 queries
def get_orders():
    orders = Order.objects.all()
    for order in orders:
        print(order.customer.name)  # Query per order!

# GOOD - Single query with join
def get_orders():
    orders = Order.objects.select_related('customer')
    for order in orders:
        print(order.customer.name)
```

### select_related vs prefetch_related

| Relationship | Method | SQL |
|-------------|--------|-----|
| ForeignKey | `select_related` | JOIN |
| OneToOneField | `select_related` | JOIN |
| ManyToManyField | `prefetch_related` | 2 queries |
| Reverse ForeignKey | `prefetch_related` | 2 queries |

```python
# Combining both
Order.objects.select_related(
    'customer',
    'customer__profile'
).prefetch_related(
    'items',
    'items__product'
)
```

### Custom Prefetch

```python
from django.db.models import Prefetch

# Only prefetch active items
Order.objects.prefetch_related(
    Prefetch(
        'items',
        queryset=OrderItem.objects.filter(status='active')
    )
)
```

## Celery Integration

### Task with Transaction Safety

```python
# services.py
from django.db import transaction

def order_complete(*, order_id: int) -> Order:
    order = Order.objects.get(id=order_id)
    order.status = 'completed'
    order.save()

    # Dispatch AFTER transaction commits
    transaction.on_commit(
        lambda: send_order_confirmation.delay(order.id)
    )

    return order
```

### Celery Task Pattern

```python
# tasks.py
from celery import shared_task

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_order_confirmation(self, order_id: int) -> None:
    try:
        order = Order.objects.get(id=order_id)
        send_email(order.customer.email, 'Order confirmed', ...)
    except Order.DoesNotExist:
        # Don't retry if order doesn't exist
        return
    except EmailError as e:
        raise self.retry(exc=e)
```

## Exception Handling

### Application Error

```python
# core/exceptions.py
class ApplicationError(Exception):
    def __init__(self, message: str, extra: dict | None = None):
        super().__init__(message)
        self.message = message
        self.extra = extra or {}
```

### Usage in Services

```python
# services.py
from core.exceptions import ApplicationError

def ingredient_analyze(*, raw_text: str) -> IngredientScan:
    if not raw_text.strip():
        raise ApplicationError(
            "Ingredient text cannot be empty",
            extra={"field": "raw_text"}
        )
    ...
```

### Exception Handler

```python
# api/exception_handlers.py
from rest_framework.views import exception_handler
from core.exceptions import ApplicationError

def custom_exception_handler(exc, context):
    if isinstance(exc, ApplicationError):
        return Response(
            {"error": exc.message, "extra": exc.extra},
            status=status.HTTP_400_BAD_REQUEST
        )
    return exception_handler(exc, context)
```

## Anti-Patterns to Avoid

1. **Business logic in views** - Use services
2. **Business logic in models** - Use services
3. **Django signals for side effects** - Use explicit service calls
4. **Fat models** - Keep models focused on data
5. **Generic ViewSets** - Use explicit APIViews
6. **save() overrides** - Use services
7. **Complex querysets in views** - Use selectors
8. **N+1 queries** - Always check with django-debug-toolbar

## Testing Pattern

```python
# tests/test_services.py
import pytest
from users.services import user_create

@pytest.mark.django_db
def test_user_create_with_valid_data():
    user = user_create(
        email="test@example.com",
        name="Test User",
        password="securepass123"
    )

    assert user.email == "test@example.com"
    assert user.name == "Test User"
    assert user.check_password("securepass123")

@pytest.mark.django_db
def test_user_create_with_duplicate_email_raises():
    user_create(email="test@example.com", name="First", password="pass123")

    with pytest.raises(ValidationError):
        user_create(email="test@example.com", name="Second", password="pass456")
```
