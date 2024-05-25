import json.encoder
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import Announcement, regions, get_chilanzar_sections
import json, time
from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User



def generate_common_choices(max_number):
    pairs = []
    last_digit = 2
    for i in range(1, max_number):
        pairs.append([i, i+1])
        last_digit = i + 1
    return [1, *pairs, last_digit]

def filter_announcements_by_floor(queryset, apartment_floor, needs_iteration=False, equal_or_greater=False):
    if (equal_or_greater):
        filtered_queryset = queryset.filter(floor__apartment_floor__gte=apartment_floor)
        return filtered_queryset
    if needs_iteration:
        filtered_queryset = queryset.filter(floor__apartment_floor__in=apartment_floor)
        return filtered_queryset
    else:
        filtered_queryset = queryset.filter(floor__apartment_floor=apartment_floor)
        return filtered_queryset

def filter_announcements(kvartal=None, roomCount=None, minStorey=None, maxStorey=None, minPrice=None, maxPrice=None, including_sales=None, including_rent=None, specific_region=None):
    queryset = Announcement.objects.all()
    appliedFilters = {}
    if including_sales and including_rent:
        pass

    if including_sales and not including_rent:
        queryset = queryset.filter(announcement_type='продается')
        appliedFilters[f'including_sales'] = True

    if not including_sales and including_rent:
        queryset = queryset.filter(announcement_type='в аренду')
        appliedFilters[f'including_rent'] = True
    
    if kvartal is not None and specific_region and specific_region == 'Чиланзар':
        queryset = queryset.filter(kvartal=kvartal)
        appliedFilters[f'kvartal'] = True
   
    if roomCount is not None:
        queryset = queryset.filter(room_count=int(roomCount)+1)
        appliedFilters[f'roomCount'] = True
   
    if minPrice is not None:
        queryset = queryset.filter(price__gte=minPrice)
        appliedFilters[f'minPrice'] = True
    
    if specific_region is not None:
        queryset = queryset.filter(apartment_region=specific_region)
        appliedFilters[f'specific_region'] = True
        
    if maxPrice is not None:
        queryset = queryset.filter(price__lte=maxPrice)
        appliedFilters[f'maxPrice'] = True

    if maxStorey:
        queryset = queryset.filter(floor__apartment_floor__lte=maxStorey)
        appliedFilters[f'maxStorey'] = True
    
    if minStorey:
        queryset = queryset.filter(floor__apartment_floor__gte=minStorey)
        appliedFilters[f'minStorey'] = True

    return queryset

def GetReiltorContact():
    reiltor = Reiltor_Number.objects.all()
    reiltor = reiltor[0] if reiltor else None
    if reiltor:
        serializedreiltor = ReiltorNumberSerializer(reiltor, many=False)
        return serializedreiltor.data
    else:
        return None

class FilteredAnnouncementsView(APIView):
    def post(self, request, format=None):
        try:
            data = json.loads(request.body) if request.body else None
            if data:
                including_sales = data.get('including_sales')
                including_rent = data.get('including_rent')
                kvartal = data.get('kvartal')
                requested_region = data.get('region_choice')
                roomMmount = data.get('amount_of_room')
                min_storey = data.get('minimum_storey')
                max_storey = data.get('maximum_storey')
                minPrice = data.get('priceMinData')
                maxPrice = data.get('priceMaxData')
                queryset = filter_announcements(kvartal=kvartal, roomCount=roomMmount, minStorey=min_storey, maxStorey=max_storey, minPrice=minPrice, maxPrice=maxPrice, including_sales=including_sales, including_rent=including_rent, specific_region=requested_region)
                serializedData = AnnouncementSerializer(queryset, many=True)
                return Response({'result': serializedData.data, 'supported_regions':regions}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AllAnnouncementRequest(APIView):
    def get(self, request, format=None):
        queryset = Announcement.objects.all()
        serializedData = AnnouncementSerializer(queryset, many=True)
        return Response({'data': serializedData.data, 'supported_regions':regions}, status=status.HTTP_200_OK)

def get_announcements_by_room_count(room_count, current_id):
    announcements = Announcement.objects.filter(room_count=room_count).exclude(id=current_id)[:8]
    return announcements

class GetAnnouncementInDetail(APIView):
    def get(self, request, product_id, format=None):
        try:
            product_object = Announcement.objects.get(id=product_id)
            serializedData = AnnouncementSerializer(product_object, many=False)
            if serializedData.data:
                room_count = serializedData.data.get('room_count')
                announcement_id = serializedData.data.get('id')
                recommended_announcements = get_announcements_by_room_count(room_count, announcement_id)
                serialized_recommendation = AnnouncementSerializer(recommended_announcements, many=True)
                reiltor = GetReiltorContact()
                return Response({'announcement':serializedData.data, 'recommendations': serialized_recommendation.data, 'reiltor':reiltor}, status=status.HTTP_200_OK)
        except:
            return Response(None, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class AnnouncementCreateView(generics.CreateAPIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    def post(self, request, *args, **kwargs):
        expected_kvartals = get_chilanzar_sections().get('indexedValue')
        id = request.data.get('id')
        price = request.data.get('price')
        description = request.data.get('description')
        thumbnail = request.FILES.getlist('thumbnail')
        all_images = request.FILES.getlist('images')
        room_count = request.data.get('room_count')
        mortgage_deal_possible = request.data.get('mortgage_deal_possible')
        located_at_edge = request.data.get('located_at_edge')
        kvartal = request.data.get('kvartal')
        kvartal = expected_kvartals.get(kvartal) if kvartal else 33
        landmark = request.data.get('landmark')
        announcement_type = request.data.get('announcement_type')
        selected_tashkent_region = request.data.get('apartment_region')
        construction_material = request.data.get('construction_material')
        room_layout = request.data.get('room_layout')
        bathroom = request.data.get('bathroom')
        building_total_floor = request.data.get('floor.building_total_floor')
        apartment_floor = request.data.get('floor.apartment_floor')
        apartment_room_count = request.data.get('floor.apartment_room_count')
        kitchen_size = request.data.get('kitchen_size')
        square_meters = request.data.get('square_meters')
        updated_instance = None

        prepared_floor = floor.objects.get_or_create(
            building_total_floor=building_total_floor,
            apartment_floor=apartment_floor,
            apartment_room_count=apartment_room_count
        )

        if id:
            announcement_instance = Announcement.objects.get(id=id)
            updated_instance = announcement_instance
            announcement_instance.price = price
            announcement_instance.description = description
            announcement_instance.square_meters = square_meters
            announcement_instance.apartment_region = selected_tashkent_region
            announcement_instance.announcement_type = announcement_type
            announcement_instance.floor = floor.objects.get_or_create(building_total_floor=building_total_floor, apartment_floor=apartment_floor, apartment_room_count=apartment_room_count)[0]
            announcement_instance.bathroom = bathroom
            announcement_instance.kitchen_size = kitchen_size
            announcement_instance.room_count = room_count
            announcement_instance.construction_material = construction_material
            announcement_instance.kvartal = kvartal
            announcement_instance.landmark = landmark
            announcement_instance.room_layout = room_layout
            announcement_instance.mortgage_deal_possible = json.loads(mortgage_deal_possible)
            announcement_instance.end_wall_structure = json.loads(located_at_edge)
            if len(thumbnail):thumbnail = thumbnail[0]
            if len(all_images):
                for each_image in all_images:
                    uploaded_image = apartment_images.objects.create(file=each_image)
                    announcement_instance.images.add(uploaded_image)
            announcement_instance.save()
        else:
            prepared_floor = floor.objects.get_or_create(
                building_total_floor=building_total_floor,
                apartment_floor=apartment_floor,
                apartment_room_count=apartment_room_count
            )
            new_announcement = Announcement.objects.create(
                price=price,
                description=description,
                thumbnail=thumbnail[0],
                square_meters=square_meters,
                apartment_region=selected_tashkent_region,
                announcement_type=announcement_type,
                floor=prepared_floor[0],
                bathroom=bathroom,
                kitchen_size=kitchen_size,
                room_count=room_count,
                construction_material=construction_material,
                kvartal=3,
                landmark=landmark,
                room_layout=room_layout,
                mortgage_deal_possible=json.loads(mortgage_deal_possible),
                end_wall_structure = json.loads(located_at_edge),
            )
            if len(all_images):
                for each_image in all_images:
                    uploaded_image = apartment_images.objects.create(file=each_image)
                    new_announcement.images.add(uploaded_image)
            updated_instance = new_announcement
        serialized_result = AnnouncementSerializer(updated_instance, many=False)
        return Response(serialized_result.data, status=status.HTTP_201_CREATED)

class AnnouncementDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            information = json.loads(request.body) if request.body else None
            if information:
                requested_announcement_id = information.get('id')
                announcement = Announcement.objects.get(id=requested_announcement_id)
                announcement.images.clear()
                serializer = AnnouncementSerializer(announcement)
                return Response(serializer.data)
        except Announcement.DoesNotExist:
            return Response({"message": "Announcement does not exist"}, status=status.HTTP_404_NOT_FOUND)
        

class ReiltorNumberView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reiltor_number = Reiltor_Number.objects.order_by('main_reiltor_number').first()
        if reiltor_number:
            serializer = ReiltorNumberSerializer(reiltor_number)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        try:
            incoming_data = json.loads(request.body) if request.body else None
            realtor_name = incoming_data.get('realtor_name')
            realtor_number = incoming_data.get('realtor_number')
            if (incoming_data):
                realtor = Reiltor_Number.objects.order_by('main_reiltor_number').first()
                realtor.main_reiltor_number = realtor_number
                realtor.reiltor_name = realtor_name
                realtor.save()
                serializer = ReiltorNumberSerializer(realtor)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response({'error': 'unknown'}, status=status.HTTP_400_BAD_REQUEST)

class DeleteAnnouncement(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            incoming_data = json.loads(request.body) if request.body else None
            announcement_id = incoming_data.get('id')
            if (announcement_id):
                requested_announcement = Announcement.objects.get(id=announcement_id)
                requested_announcement.delete()
                return Response({}, status=status.HTTP_202_ACCEPTED)
        except:
            return Response({'error': 'unknown'}, status=status.HTTP_400_BAD_REQUEST)

class ObtainExpiringToken(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise AuthenticationFailed('Username and password are required.')

        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            raise AuthenticationFailed('Invalid username or password.')

        token, created = Token.objects.get_or_create(user=user)

        expiration_date = timezone.now() + timedelta(days=7)
        token.created = timezone.now()
        token.expiration_date = expiration_date
        token.save()
        return Response({'token': token.key})
    

class ManageClientNumbers(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        client_numbers_objects = client_numbers.objects.all()
        serializer = ClientNumbersSerializer(client_numbers_objects, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClientNumbersSerializer(data=json.loads(request.body))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendMessagesToClients(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        incoming_data = json.loads(request.body) if request.body else None
        if incoming_data:
            test_only = incoming_data.get('test_mode')
            text_message = incoming_data.get('message')
            print(test_only)
            print(text_message)
            return Response({}, status=status.HTTP_200_OK)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

class PurgeNumber(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            incoming_data = json.loads(request.body) if request.body else None
            if incoming_data:
                requested_id = incoming_data.get('id')
                requested_number =client_numbers.objects.get(id=requested_id)
                requested_number.delete()
                return Response({}, status=status.HTTP_200_OK)
        except:
            return Response({}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)