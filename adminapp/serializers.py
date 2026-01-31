from rest_framework import serializers

class TodaysSpecialSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    can_be_booked = serializers.SerializerMethodField()
    item_source = serializers.SerializerMethodField()  # Add this line

    class Meta:
        model = None  # Will set dynamically
        fields = ['id', 'name', 'image', 'image_url', 'rate', 'item_per_plate', 'category', 'category_name', 'date', 'created_at', 'can_be_booked', 'item_source']
    
    def __init__(self, *args, **kwargs):
        from .models import TodaysSpecial
        self.Meta.model = TodaysSpecial
        super().__init__(*args, **kwargs)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None
    
    def get_can_be_booked(self, obj):
        # Today's special items can be booked through:
        # 1. Admin outsider booking
        # 2. TABLE_HOME_FOOD_COUNTER booking type
        return {
            "by_users_prebooked": False,
            "by_users_table_only": True,
            "by_admin": True,
            "message": "Available through: 1) Admin outsider booking, 2) TABLE_ONLY booking"
        }
    
    def get_item_source(self, obj):
        return "Today's Special"  # Always returns this for TodaysSpecial items