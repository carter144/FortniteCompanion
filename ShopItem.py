class ShopItem:
    def __init__(self, name, item_type, background_image_url, attachment_id):
        self.name = name
        self.item_type = item_type
        self.background_image_url = background_image_url
        # Attachment ID is for facebook to reuse images
        self.attachment_id = attachment_id