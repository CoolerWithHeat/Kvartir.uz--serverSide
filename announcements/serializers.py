from rest_framework import serializers, viewsets
from .models import Announcement, apartment_images, floor, Reiltor_Number, client_numbers

class ApartmentImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = apartment_images
        fields = '__all__'

class FloorSerializer(serializers.ModelSerializer):
    class Meta:
        model = floor
        fields = '__all__'

class AnnouncementSerializer(serializers.ModelSerializer):
    images = ApartmentImagesSerializer(many=True)
    floor = FloorSerializer()

    class Meta:
        model = Announcement
        fields = '__all__'

class AnnouncementViewSet(viewsets.ModelViewSet):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer

class ReiltorNumberSerializer(serializers.ModelSerializer):
    secondary_numbers = serializers.SerializerMethodField()

    class Meta:
        model = Reiltor_Number
        fields = ['reiltor_name', 'main_reiltor_number', 'secondary_numbers']

    def get_secondary_numbers(self, obj):
        return [phone.number for phone in obj.secondary_numbers.all()]
    
class ReiltorNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reiltor_Number
        fields = ['reiltor_name', 'main_reiltor_number', 'secondary_numbers']

class ClientNumbersSerializer(serializers.ModelSerializer):
    class Meta:
        model = client_numbers
        fields = ['id', 'number']