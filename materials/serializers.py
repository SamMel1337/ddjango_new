from rest_framework import generics, permissions
from rest_framework import serializers
from .models import Course, Lesson, Subscription
from .models import Product, Price, Payment
from .validators import ExternalLinkValidator


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['user', 'stripe_session_id', 'status']

class LessonSerializer(serializers.ModelSerializer):
    def validate_video_url(self, value):
        if value:
            validator = ExternalLinkValidator('video_url')
            validator(value)
        return value

    class Meta:
        model = Lesson
        fields = '__all__'



class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(
                user=request.user,
                course=obj,
                is_active=True
            ).exists()
        return False

    def get_lessons_count(self, obj):
        return obj.lessons.count()

class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = '__all__'
        read_only_fields = ['user', 'subscribed_at']
class CreatePaymentSerializer(serializers.Serializer):
    course_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


