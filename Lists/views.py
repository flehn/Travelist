from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.decorators import APIView, api_view, permission_classes
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)
from rest_framework.request import Request
from rest_framework.response import Response


from .models import TList, Element
from rest_framework import viewsets
from .serializer import ListSerializer, ElementSerializer

@login_required
@api_view(['POST'])
def create_list_with_element(request):

    if request.method == 'POST':
        list_data = request.data.get('list')
        element_data = request.data.get('elements')

        list_serializer = ListSerializer(data=list_data)
        if list_serializer.is_valid():
            list_serializer.save()

            #Directly use the saved list to get its ID:
            list_id = list_serializer.instance

            # create key-value pair to add the list_id
            list_id_dict = {"tlist": list_id.id}
            

            added_elements = [] #For Debugging purposes only, so we can return the Response with the added elements (Line 50).
            for element in element_data:
                #Add the missing list_id to each element. [{"name":"Cafe"}, {"name":"Club"}] -> [{"name":"Cafe", {"tlist": list_id.id}}, {"name":"Club"}, {"tlist": list_id.id}]
                element.update(list_id_dict)

                element_serializer = ElementSerializer(data=element)
                if element_serializer.is_valid():
                    element_serializer.save()
                    added_elements.append(element)
            return Response({'list': list_serializer.data, 'elements': added_elements}, status=status.HTTP_201_CREATED)


        return Response(list_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


'''
Get a list 
'''

@api_view(['GET'])
def get_list_with_elements(request, list_id):
    try:
        list_instance = TList.objects.get(id=list_id)
        list_serializer = ListSerializer(list_instance)
        
        # Manually fetch and serialize the elements
        elements = Element.objects.filter(tlist_id=list_id)
        elements_serializer = ElementSerializer(elements, many=True)

        # Add the serialized elements to the list's response data
        response_data = list_serializer.data
        response_data['elements'] = elements_serializer.data

        return Response(response_data)
    
    except TList.DoesNotExist:
        return Response({'error': 'List not found'}, status=404)
    
'''
Delete a list!
'''

@login_required
@api_view(['DELETE'])
def delete_list(request, list_id):
    try:
        list_to_delete = TList.objects.get(id=list_id)
        list_to_delete.delete()
        return Response({'message': 'List deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    except TList.DoesNotExist:
        return Response({'error': 'List not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


'''
Updating a list or its elements:

• Updating attributes of the list itself.
• Adding new elements to the list.
• Updating or deleting existing elements.
'''

@login_required
@api_view(['PUT'])
def update_list(request, list_id):
    try:
        list_to_update = TList.objects.get(id=list_id)

        # Update list attributes
        list_data = request.data.get('list')
        list_serializer = ListSerializer(list_to_update, data=list_data, partial=True)
        if list_serializer.is_valid():
            list_serializer.save()

            # Update elements
            elements_data = request.data.get('elements')
            updated_elements = []
            for element_data in elements_data:
                element_id = element_data.get('id')
                if element_id:
                    # Update existing element
                    element = Element.objects.get(id=element_id, tlist=list_id)
                    element_serializer = ElementSerializer(element, data=element_data, partial=True)
                else:
                    # Create new element
                    element_data['tlist'] = list_id
                    element_serializer = ElementSerializer(data=element_data)

                if element_serializer.is_valid():
                    element_serializer.save()
                    updated_elements.append(element_serializer.data)
                else:
                    return Response(element_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'list': list_serializer.data, 'elements': updated_elements}, status=status.HTTP_200_OK)

        return Response(list_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except TList.DoesNotExist:
        return Response({'error': 'List not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








@login_required
@api_view(['POST'])
def like_list(request, list_id):
    '''
    this function adds the like function, a user can like a list, if he clicks again, his like is removed. 
    Only Logged In users can like a list. 
    '''
    if request.method == 'POST':
        user = request.user
        list_id = request.data.get('list_id')
        list_obj = TList.objects.get(id=list_id)

        if user in list_obj.likes.all():
            list_obj.likes.remove(user)
            liked = False
        else:
            list_obj.likes.add(user)
            liked = True

        return JsonResponse({'liked': liked, 'likes_count': list_obj.likes.count()})

    return JsonResponse({'error': 'Invalid request'}, status=400)