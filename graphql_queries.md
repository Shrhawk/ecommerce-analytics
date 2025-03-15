# GraphQL Queries Documentation

This document contains all available GraphQL queries for the e-commerce API. You can test these queries in the GraphQL Playground at `http://localhost:8000/graphql`.

## Table of Contents
- [Products](#products)
  - [Get Single Product](#get-single-product)
  - [Get Product List](#get-product-list)
- [Categories](#categories)
  - [Get Single Category](#get-single-category)
  - [Get Categories List](#get-categories-list)
- [Orders](#orders)
  - [Get Single Order](#get-single-order)
- [Customers](#customers)
  - [Get Customer Details](#get-customer-details)
- [Analytics](#analytics)
  - [Get Daily Sales](#get-daily-sales)

## Products

### Get Single Product

Get detailed information about a specific product:

```graphql
query GetProduct($productId: Int!) {
  product(productId: $productId) {
    productId
    name
    description
    price
    cost
    profitMargin
    inventoryCount
    sku
    weight
    isActive
    nameCategory
    category {
      name
      description
    }
  }
}
```

Variables:
```json
{
  "productId": 1
}
```

### Get Product List

Get a list of products with optional filtering:

```graphql
query GetProducts(
  $skip: Int, 
  $limit: Int, 
  $categoryId: Int, 
  $isActive: Boolean
) {
  products(
    skip: $skip, 
    limit: $limit, 
    categoryId: $categoryId, 
    isActive: $isActive
  ) {
    productId
    name
    price
    nameCategory
    inventoryCount
    isActive
    profitMargin
    category {
      name
      description
    }
  }
}
```

Variables:
```json
{
  "skip": 0,
  "limit": 10,
  "categoryId": null,
  "isActive": true
}
```

## Categories

### Get Single Category

Get detailed information about a specific category:

```graphql
query GetCategory($categoryId: Int!) {
  category(categoryId: $categoryId) {
    categoryId
    name
    description
    parentId
    createdAt
  }
}
```

Variables:
```json
{
  "categoryId": 1
}
```

### Get Categories List

Get a list of categories with optional parent filtering:

```graphql
query GetCategories($skip: Int, $limit: Int, $parentId: Int) {
  categories(skip: $skip, limit: $limit, parentId: $parentId) {
    categoryId
    name
    description
    parentId
    createdAt
  }
}
```

Variables:
```json
{
  "skip": 0,
  "limit": 10,
  "parentId": null
}
```

## Orders

### Get Single Order

Get detailed information about a specific order including items and customer:

```graphql
query GetOrder($orderId: Int!) {
  order(orderId: $orderId) {
    orderId
    orderDate
    status
    paymentMethod
    shippingAddress
    shippingCity
    shippingState
    shippingZip
    shippingCountry
    processingDate
    shippingDate
    deliveryDate
    totalAmount
    total
    profit
    quantity
    customer {
      firstName
      lastName
      email
    }
    orderItems {
      orderItemId
      quantity
      price
      discount
      total
      product {
        name
        price
      }
    }
  }
}
```

Variables:
```json
{
  "orderId": 1
}
```

## Customers

### Get Customer Details

Get detailed information about a customer including their metrics:

```graphql
query GetCustomer($customerId: Int!) {
  customer(customerId: $customerId) {
    customerId
    email
    firstName
    lastName
    streetAddress
    city
    state
    zipCode
    country
    phone
    registrationDate
    lastLogin
    totalOrders
    lifetimeValue
    firstOrderDate
    lastOrderDate
    averageOrderValue
    daysBetweenOrders
  }
}
```

Variables:
```json
{
  "customerId": 1
}
```

## Analytics

### Get Daily Sales

Get daily sales aggregation data with optional category filtering:

```graphql
query GetDailySales($startDate: Date!, $endDate: Date!, $categoryId: Int) {
  dailySales(
    startDate: $startDate, 
    endDate: $endDate, 
    categoryId: $categoryId
  ) {
    orderDate
    unitsSold
    revenue
    orderCount
    avgUnitPrice
    product {
      name
      price
      category {
        name
      }
    }
    category {
      name
      description
    }
  }
}
```

Variables:
```json
{
  "startDate": "2024-01-01",
  "endDate": "2024-03-15",
  "categoryId": null
}
```

## GraphQL Playground

1. The playground is available at `http://localhost:8000/graphql`
2. You can write your query in the left panel
3. Variables should be provided in the "Variables" panel at the bottom
4. Click the "Play" button or press Ctrl+Enter to execute the query
5. Results will appear in the right panel
6. Use the "Docs" panel on the right to explore the schema
7. The playground provides auto-completion and validation
