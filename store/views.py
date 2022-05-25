from django.shortcuts import get_object_or_404
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status

from .pagination import DefaultPagination
from .models import OrderItem, Product, Collection, Review
from .serializers import CollectionSerializer, ProductSerializer, ReviewSerializer
from .filters import ProductFilter


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    filter_class = ProductFilter
    pagination_class = DefaultPagination

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product can not be deleted because it is associated with an order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products'))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.annotate(
            products_count=Count('products')), pk=pk)
        if collection.products.count() > 0:
            return Response({
                'error': 'Collection cannot be deleted because it includes one or more products.'
            })
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    # @api_view(['GET', 'POST'])
    # def product_list(request):
    #     if request.method == 'GET':
    #         queryset = Product.objects.select_related('collection').all()
    #         serializer = ProductSerializer(queryset, many=True)
    #         return Response(serializer.data)
    #     elif request.method == 'POST':
    #         serializer = ProductSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #         if serializer.is_valid():
    #             serializer.validated_data
    #             return Response('ok')
    #         else:
    #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @api_view()
    # def product_detail(request, id):
    #     try:
    #         product = Product.objects.get(pk=id)
    #         serializer = ProductSerializer(product)
    #         return Response(serializer.data)
    #     except Product.DoesNotExist:
    #         return Response(status=status.HTTP_404_NOT_FOUND)

    # @api_view(['GET', 'PUT', 'DELETE'])
    # def product_detail(request, id):
    #     product = get_object_or_404(Product, pk=id)
    #     if request.method == 'GET':
    #         serializer = ProductSerializer(product)
    #         return Response(serializer.data)
    #     elif request.method == 'PUT':
    #         serializer = ProductSerializer(product, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)
    #     elif request.method == 'DELETE':
    #         if product.orderitems.count() > 0:
    #             return Response({'error': 'Product can not be deleted because it is associated with an order item'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #         product.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)

    # @api_view(['GET', 'POST'])
    # def collection_list(request):
    #     if request.method == 'GET':
    #         queryset = Collection.objects.annotate(
    #             products_count=Count('products')).all()
    #         serializer = CollectionSerializer(queryset, many=True)
    #         return Response(serializer.data)
    #     elif request.method == 'POST':
    #         serializer = CollectionSerializer(data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @api_view(['GET', 'PUT', 'DELETE'])
    # def collection_detail(request, pk):
    #     collection = get_object_or_404(Collection.objects.annotate(
    #         products_count=Count('products')), pk=pk)
    #     if request.method == 'GET':
    #         serializer = CollectionSerializer(collection)
    #         return Response(serializer.data)
    #     elif request.method == 'PUT':
    #         serializer = CollectionSerializer(collection, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)
    #     elif request.method == 'DELETE':
    #         if collection.products.count() > 0:
    #             return Response({
    #                 'error': 'Collection cannot be deleted because it includes one or more products.'
    #             })
    #         collection.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
