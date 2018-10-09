import os


def get_document_upload_path(instance, filename):
    # Util method to calculate filesystem upload path for document
    return os.path.join(instance.product.name, 'documents', filename)


def get_images_upload_path(instance, filename):
    # Util method to calculate filesystem image path
    from psc.product.models import Image
    folders_map = {
        Image.CROP_TYPE_THUMBNAIL: 'thumbnail',
        Image.CROP_TYPE_LISTING: 'listing',
        Image.CROP_TYPE_PRODUCT: 'detail',
        Image.CROP_TYPE_COMPANY: 'company'
    }

    return os.path.join(instance.product.name if hasattr(instance, 'product') else instance.company.name,
                        'images', folders_map[instance.crop_type], filename)
