# Version 1.3.0

**Added:**

- Added `DjangoValidationErrorTransformMixin` mixin

**Removed:**

- Removed `APIErrorsMixin` mixin

# Version 1.2.2

**Added:**

- Split `UpdateModelMixin` into two mixins: `FullUpdateModelMixin` and `PartialUpdateModelMixin`

# Version 1.2.1

**Added:**

- Added `get_field_name` public method to `ErrorsFormatter` class

# Version 1.2.0

**Added:**

- Added action-based permissions for ViewSets

# Version 1.1.0

**Added:**

- Added ability for GenericAPIViews to have two serializers per request/response cycle


# Version 1.0.0

**Added:**

- Added action-based serializers for ViewSets
- Added ability for ViewSets to have two serializers per request/response cycle
- Added single format for all errors
