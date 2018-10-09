
def get_created_updated_objects_by_user(date, user, obj_class):
    # Util method to get created or updated objects
    # of given class by given user and date
    created_objects = obj_class.objects.filter(
        created_by=user,
        created_at__contains=date,
        is_approved=False
    )

    updated_objects = obj_class.objects.filter(
        edited_by=user,
        edited_at__contains=date,
        is_approved=False
    )
    return created_objects, updated_objects
