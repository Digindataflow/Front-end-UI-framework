from rest_framework import serializers
from toys.models import Toy

class ToySerializer(serializers.ModelSerializer):

    class Meta:
        model = Toy
        exclude = ('created',)