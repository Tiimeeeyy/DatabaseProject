### **Software Requirements**

#### **Menu Presentation**
- The menu must include at least 10 distinct pizzas, featuring at least 10 different ingredients, along with 4 drinks and 2 desserts.
#### **Order Processing**
- **Customer Information Management**: Store essential customer information such as name, gender, birthdate, phone number, and address. This information is crucial for order confirmation and delivery.
- **Order Confirmation**: Upon placing an order, customers should receive a confirmation with details of their order and an estimated delivery time.
- **Restaurant Monitoring**: Provide a real-time display for the restaurant staff, showing a list of pizzas that have been ordered but not yet dispatched for delivery.
- **Earnings Report**: Generate a monthly earnings report for the restaurant, with filtering options based on region (postal code or city), customer gender, and age.

#### **Order Delivery**

Delivery management is another crucial component, involving:

- **Delivery Status**: Allow customers to check the current status of their order (e.g., being prepared, in process, out for delivery) and estimated delivery time.
- **Order Cancellation**: Customers should be able to cancel their order within 5 minutes of placing it.
- **Delivery Personnel Management**:

- The restaurant employs several delivery persons, each assigned to a specific postal code area.
- A delivery person can only deliver within their assigned area. Multiple delivery persons can be assigned to the same postal code if needed.
- Once a delivery is initiated, the delivery person is unavailable for further deliveries for 30 minutes.
- The system must handle the delivery timing logic, including the ability to group multiple orders for the same postal code into a single delivery if they occur within the 5-minute window.