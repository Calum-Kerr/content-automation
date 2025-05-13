# Creating Self-Calculating PDF Invoices and Order Forms

Self-calculating PDF invoices and order forms represent one of the most practical and valuable applications of interactive PDF technology. These intelligent documents automatically perform calculations as users enter data, eliminating manual calculation errors, saving time, and creating a more professional experience for both businesses and customers.

This comprehensive guide explores the principles and techniques for creating effective self-calculating PDF invoices and order forms, from basic calculations to sophisticated features that streamline the ordering and billing process.

## Why Create Self-Calculating PDF Forms?

Before diving into specific techniques, let's understand the benefits of automated calculations:

### Advantages of Self-Calculating Documents

1. **Error Reduction and Accuracy**:
   - Eliminate manual calculation mistakes
   - Ensure mathematical precision
   - Prevent transcription errors
   - Maintain formula consistency
   - Guarantee correct totals and subtotals

2. **Time and Efficiency Savings**:
   - Automate repetitive calculations
   - Reduce form completion time
   - Minimize verification needs
   - Speed up processing and approval
   - Enable instant updates when quantities change

3. **Professional Image and User Experience**:
   - Present a modern, tech-savvy business image
   - Provide immediate feedback to customers
   - Create confidence in accuracy
   - Reduce customer support inquiries
   - Enhance overall customer experience

### Common Applications and Use Cases

1. **Business Documents**:
   - Customer invoices and billing
   - Price quotes and estimates
   - Purchase orders
   - Service agreements with variable pricing
   - Subscription or recurring billing forms

2. **Sales and Order Processing**:
   - Product order forms
   - Service booking forms
   - Event registration with tiered pricing
   - Customizable product configurations
   - Package selection with options

3. **Financial and Accounting**:
   - Expense reports
   - Budget planning documents
   - Financial calculators
   - Tax forms and worksheets
   - Payment schedules

## Planning Your Self-Calculating Form

Effective preparation for successful implementation:

### Identifying Calculation Requirements

1. **Determining Calculation Needs**:
   - Identify all mathematical operations needed
   - Map relationships between fields
   - Define calculation sequence and dependencies
   - Determine conditional calculations
   - Plan for special cases and exceptions

2. **Data Input Planning**:
   - Identify all user input fields
   - Determine appropriate field types
   - Plan for validation requirements
   - Consider default values
   - Design for ease of data entry

3. **Output and Results Planning**:
   - Define calculation result fields
   - Plan formatting for monetary values
   - Determine rounding rules
   - Consider subtotals and summary fields
   - Plan for data extraction and processing

### Designing the Form Layout

1. **Organizing Information Logically**:
   - Group related items together
   - Create clear visual separation between sections
   - Establish natural data entry flow
   - Position calculation results appropriately
   - Consider both screen and print layouts

2. **Line Item Structure**:
   - Design consistent row format for items
   - Include quantity, description, price fields
   - Add line total calculations
   - Consider space for multiple items
   - Plan for variable item counts

3. **Summary Section Design**:
   - Create clear subtotal area
   - Include tax, shipping, discount sections
   - Design prominent grand total display
   - Add payment information section
   - Include terms and conditions area

### Planning for Different Scenarios

1. **Variable Item Quantities**:
   - Fixed vs. variable number of line items
   - Handling minimum/maximum quantities
   - Showing/hiding rows based on needs
   - Scrolling vs. pagination for many items
   - Maintaining calculations across pages

2. **Discounts and Special Pricing**:
   - Percentage vs. fixed amount discounts
   - Quantity-based pricing tiers
   - Special customer pricing
   - Promotional code handling
   - Conditional discount application

3. **Taxes and Additional Charges**:
   - Multiple tax rates or categories
   - Regional tax variations
   - Shipping and handling calculations
   - Additional fees and surcharges
   - Conditional charges based on selections

## Creating Basic Self-Calculating Forms

Implementing fundamental calculation functionality:

### Setting Up Line Item Calculations

1. **Creating Line Item Structure**:
   - Add text fields for quantities
   - Create fields for unit prices
   - Add description fields
   - Create line total calculation fields
   - Format fields appropriately

2. **Basic Line Calculations**:
   ```javascript
   // Calculate line total (quantity × price)
   var quantity = this.getField("quantity1").value;
   var price = this.getField("price1").value;
   
   // Convert to numbers and calculate
   quantity = parseFloat(quantity) || 0;
   price = parseFloat(price) || 0;
   
   // Set the result with 2 decimal places
   event.value = (quantity * price).toFixed(2);
   ```

3. **Implementing Multiple Line Items**:
   - Create consistent field naming (item1, item2, etc.)
   - Implement calculation for each line
   - Consider using arrays or loops for many lines
   - Test with various input combinations
   - Verify calculations across all lines

### Creating Subtotals and Totals

1. **Calculating Subtotals**:
   ```javascript
   // Sum all line totals
   var subtotal = 0;
   
   // Loop through line items (assuming fields named lineTotal1, lineTotal2, etc.)
   for (var i = 1; i <= 10; i++) {
     var lineField = "lineTotal" + i;
     if (this.getField(lineField)) {
       var lineValue = parseFloat(this.getField(lineField).value) || 0;
       subtotal += lineValue;
     }
   }
   
   event.value = subtotal.toFixed(2);
   ```

2. **Tax Calculations**:
   ```javascript
   // Calculate tax based on subtotal
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var taxRate = parseFloat(this.getField("taxRate").value) || 0;
   
   // Convert tax rate from percentage to decimal
   taxRate = taxRate / 100;
   
   // Calculate tax amount
   var taxAmount = subtotal * taxRate;
   
   event.value = taxAmount.toFixed(2);
   ```

3. **Grand Total Calculation**:
   ```javascript
   // Calculate final total
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var tax = parseFloat(this.getField("taxAmount").value) || 0;
   var shipping = parseFloat(this.getField("shipping").value) || 0;
   
   // Sum all components
   var grandTotal = subtotal + tax + shipping;
   
   event.value = grandTotal.toFixed(2);
   ```

### Implementing Discounts

1. **Percentage Discount Calculation**:
   ```javascript
   // Calculate discount amount based on percentage
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var discountPercent = parseFloat(this.getField("discountPercent").value) || 0;
   
   // Convert percentage to decimal and calculate
   var discountAmount = subtotal * (discountPercent / 100);
   
   event.value = discountAmount.toFixed(2);
   ```

2. **Fixed Amount Discounts**:
   ```javascript
   // Apply fixed discount amount
   var discountAmount = parseFloat(this.getField("discountAmount").value) || 0;
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   
   // Ensure discount doesn't exceed subtotal
   if (discountAmount > subtotal) {
     discountAmount = subtotal;
     this.getField("discountAmount").value = subtotal.toFixed(2);
   }
   
   // Calculate discounted subtotal
   var discountedSubtotal = subtotal - discountAmount;
   
   event.value = discountedSubtotal.toFixed(2);
   ```

3. **Conditional Discounts**:
   ```javascript
   // Apply discount based on order value
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var discountPercent = 0;
   
   // Set discount tier based on subtotal
   if (subtotal >= 1000) {
     discountPercent = 15; // 15% for orders $1000+
   } else if (subtotal >= 500) {
     discountPercent = 10; // 10% for orders $500-999
   } else if (subtotal >= 250) {
     discountPercent = 5;  // 5% for orders $250-499
   }
   
   // Calculate discount amount
   var discountAmount = subtotal * (discountPercent / 100);
   
   // Update discount fields
   this.getField("discountPercent").value = discountPercent;
   this.getField("discountAmount").value = discountAmount.toFixed(2);
   ```

## Advanced Calculation Features

Sophisticated functionality for professional forms:

### Quantity-Based Pricing Tiers

1. **Implementing Price Breaks**:
   ```javascript
   // Adjust unit price based on quantity
   var quantity = parseFloat(this.getField("quantity1").value) || 0;
   var basePrice = 29.99; // Standard unit price
   var unitPrice;
   
   // Apply quantity discounts
   if (quantity >= 100) {
     unitPrice = basePrice * 0.80; // 20% off for 100+
   } else if (quantity >= 50) {
     unitPrice = basePrice * 0.85; // 15% off for 50-99
   } else if (quantity >= 25) {
     unitPrice = basePrice * 0.90; // 10% off for 25-49
   } else if (quantity >= 10) {
     unitPrice = basePrice * 0.95; // 5% off for 10-24
   } else {
     unitPrice = basePrice; // Regular price
   }
   
   // Update unit price field and calculate line total
   this.getField("unitPrice1").value = unitPrice.toFixed(2);
   this.getField("lineTotal1").value = (quantity * unitPrice).toFixed(2);
   ```

2. **Displaying Tier Information**:
   ```javascript
   // Show applicable price tier information
   var quantity = parseFloat(this.getField("quantity1").value) || 0;
   var tierInfo = "";
   
   if (quantity >= 100) {
     tierInfo = "Tier 1 Pricing: 20% discount applied";
   } else if (quantity >= 50) {
     tierInfo = "Tier 2 Pricing: 15% discount applied";
   } else if (quantity >= 25) {
     tierInfo = "Tier 3 Pricing: 10% discount applied";
   } else if (quantity >= 10) {
     tierInfo = "Tier 4 Pricing: 5% discount applied";
   } else {
     tierInfo = "Standard pricing (no quantity discount)";
   }
   
   this.getField("pricingTier").value = tierInfo;
   ```

3. **Creating Tier Selection Controls**:
   ```javascript
   // Allow manual tier selection with price adjustment
   var selectedTier = this.getField("pricingTier").value;
   var basePrice = parseFloat(this.getField("basePrice").value) || 0;
   var discountedPrice;
   
   // Apply selected tier discount
   switch (selectedTier) {
     case "Tier 1 (20% off)":
       discountedPrice = basePrice * 0.80;
       break;
     case "Tier 2 (15% off)":
       discountedPrice = basePrice * 0.85;
       break;
     case "Tier 3 (10% off)":
       discountedPrice = basePrice * 0.90;
       break;
     case "Tier 4 (5% off)":
       discountedPrice = basePrice * 0.95;
       break;
     default:
       discountedPrice = basePrice;
   }
   
   this.getField("discountedPrice").value = discountedPrice.toFixed(2);
   ```

### Tax Handling for Different Jurisdictions

1. **Multiple Tax Rate Support**:
   ```javascript
   // Apply tax based on selected jurisdiction
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var jurisdiction = this.getField("taxJurisdiction").value;
   var taxRate = 0;
   
   // Set tax rate based on jurisdiction
   switch (jurisdiction) {
     case "New York":
       taxRate = 8.875;
       break;
     case "California":
       taxRate = 7.25;
       break;
     case "Texas":
       taxRate = 6.25;
       break;
     case "Florida":
       taxRate = 6.0;
       break;
     default:
       taxRate = 0;
   }
   
   // Update tax rate field and calculate tax
   this.getField("taxRate").value = taxRate;
   var taxAmount = subtotal * (taxRate / 100);
   this.getField("taxAmount").value = taxAmount.toFixed(2);
   ```

2. **Tax Category Handling**:
   ```javascript
   // Calculate tax based on product categories
   var subtotal1 = parseFloat(this.getField("subtotalCategory1").value) || 0; // Taxable goods
   var subtotal2 = parseFloat(this.getField("subtotalCategory2").value) || 0; // Services
   var subtotal3 = parseFloat(this.getField("subtotalCategory3").value) || 0; // Tax-exempt
   
   var taxRate1 = parseFloat(this.getField("taxRateGoods").value) || 0;
   var taxRate2 = parseFloat(this.getField("taxRateServices").value) || 0;
   
   // Calculate tax for each category
   var tax1 = subtotal1 * (taxRate1 / 100);
   var tax2 = subtotal2 * (taxRate2 / 100);
   var tax3 = 0; // No tax on exempt items
   
   // Update tax fields
   this.getField("taxCategory1").value = tax1.toFixed(2);
   this.getField("taxCategory2").value = tax2.toFixed(2);
   this.getField("taxCategory3").value = tax3.toFixed(2);
   
   // Calculate total tax
   var totalTax = tax1 + tax2 + tax3;
   this.getField("totalTax").value = totalTax.toFixed(2);
   ```

3. **Tax Exemption Handling**:
   ```javascript
   // Handle tax exemption status
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var taxExempt = this.getField("taxExempt").value;
   var taxRate = parseFloat(this.getField("taxRate").value) || 0;
   
   // Calculate tax based on exemption status
   var taxAmount = 0;
   
   if (taxExempt != "Yes") {
     taxAmount = subtotal * (taxRate / 100);
     this.getField("taxExemptID").display = display.hidden;
   } else {
     this.getField("taxExemptID").display = display.visible;
   }
   
   this.getField("taxAmount").value = taxAmount.toFixed(2);
   ```

### Shipping and Handling Calculations

1. **Weight-Based Shipping**:
   ```javascript
   // Calculate shipping based on total weight
   var weight1 = parseFloat(this.getField("weight1").value) || 0;
   var weight2 = parseFloat(this.getField("weight2").value) || 0;
   var weight3 = parseFloat(this.getField("weight3").value) || 0;
   
   // Calculate total weight
   var totalWeight = weight1 + weight2 + weight3;
   this.getField("totalWeight").value = totalWeight.toFixed(2);
   
   // Calculate shipping cost based on weight
   var shippingCost = 0;
   
   if (totalWeight <= 0) {
     shippingCost = 0;
   } else if (totalWeight <= 1) {
     shippingCost = 5.99;
   } else if (totalWeight <= 5) {
     shippingCost = 8.99;
   } else if (totalWeight <= 10) {
     shippingCost = 12.99;
   } else {
     shippingCost = 12.99 + (Math.ceil(totalWeight - 10) * 1.50);
   }
   
   this.getField("shippingCost").value = shippingCost.toFixed(2);
   ```

2. **Order Value-Based Shipping**:
   ```javascript
   // Calculate shipping based on order value
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var shippingCost = 0;
   
   // Determine shipping cost based on order value
   if (subtotal >= 100) {
     shippingCost = 0; // Free shipping for orders over $100
   } else if (subtotal >= 50) {
     shippingCost = 4.99;
   } else if (subtotal >= 25) {
     shippingCost = 7.99;
   } else {
     shippingCost = 9.99;
   }
   
   // Update shipping field and note
   this.getField("shippingCost").value = shippingCost.toFixed(2);
   
   if (shippingCost === 0) {
     this.getField("shippingNote").value = "Free Shipping Applied!";
   } else {
     this.getField("shippingNote").value = "";
   }
   ```

3. **Shipping Method Selection**:
   ```javascript
   // Calculate shipping based on selected method
   var shippingMethod = this.getField("shippingMethod").value;
   var subtotal = parseFloat(this.getField("subtotal").value) || 0;
   var shippingCost = 0;
   
   // Set shipping cost based on method
   switch (shippingMethod) {
     case "Standard (5-7 days)":
       shippingCost = 5.99;
       break;
     case "Expedited (2-3 days)":
       shippingCost = 12.99;
       break;
     case "Overnight":
       shippingCost = 24.99;
       break;
     case "Local Pickup":
       shippingCost = 0;
       break;
   }
   
   // Apply free shipping for large orders
   if (subtotal >= 100 && shippingMethod === "Standard (5-7 days)") {
     shippingCost = 0;
     this.getField("shippingNote").value = "Free Standard Shipping Applied!";
   } else {
     this.getField("shippingNote").value = "";
   }
   
   this.getField("shippingCost").value = shippingCost.toFixed(2);
   ```

## Creating Professional Invoice Templates

Designing effective, reusable invoice documents:

### Essential Invoice Components

1. **Business Information Section**:
   - Company name, logo, and contact details
   - Business address and registration numbers
   - Tax identification numbers
   - Contact person information
   - Payment terms and methods

2. **Customer Information Fields**:
   - Customer name and ID fields
   - Billing and shipping address sections
   - Contact person and details
   - Customer reference numbers
   - Account information fields

3. **Invoice Details Section**:
   - Invoice number and date fields
   - Order reference and purchase order numbers
   - Payment due date calculation
   - Terms and conditions reference
   - Invoice status indicator

### Line Item Table Design

1. **Creating Flexible Line Item Tables**:
   - Consistent column structure (item, description, quantity, price, total)
   - Appropriate field sizing for each column
   - Clear header row with column labels
   - Sufficient rows for typical orders
   - Show/hide functionality for unused rows

2. **Line Item Calculation Implementation**:
   ```javascript
   // Document-level function for line calculations
   function calculateLineTotal(row) {
     // Get field values
     var qtyField = "quantity" + row;
     var priceField = "unitPrice" + row;
     var totalField = "lineTotal" + row;
     
     var qty = parseFloat(this.getField(qtyField).value) || 0;
     var price = parseFloat(this.getField(priceField).value) || 0;
     
     // Calculate and update line total
     var total = qty * price;
     this.getField(totalField).value = total.toFixed(2);
     
     // Recalculate invoice totals
     calculateInvoiceTotals();
   }
   ```

3. **Dynamic Row Management**:
   ```javascript
   // Show/hide rows based on needed quantity
   function updateVisibleRows() {
     var rowCount = parseInt(this.getField("rowCount").value) || 5;
     
     // Limit to maximum available rows
     if (rowCount > 20) rowCount = 20;
     
     // Show/hide rows based on count
     for (var i = 1; i <= 20; i++) {
       var isVisible = (i <= rowCount);
       
       // Toggle visibility of all fields in this row
       this.getField("item" + i).display = isVisible ? display.visible : display.hidden;
       this.getField("description" + i).display = isVisible ? display.visible : display.hidden;
       this.getField("quantity" + i).display = isVisible ? display.visible : display.hidden;
       this.getField("unitPrice" + i).display = isVisible ? display.visible : display.hidden;
       this.getField("lineTotal" + i).display = isVisible ? display.visible : display.hidden;
     }
   }
   ```

### Summary Section Design

1. **Creating the Totals Area**:
   - Clear subtotal display
   - Tax calculation section
   - Discount area with options
   - Shipping and additional charges
   - Prominent grand total display

2. **Comprehensive Total Calculation**:
   ```javascript
   // Calculate all invoice totals
   function calculateInvoiceTotals() {
     // Calculate subtotal from line items
     var subtotal = 0;
     for (var i = 1; i <= 20; i++) {
       if (this.getField("lineTotal" + i)) {
         var lineValue = parseFloat(this.getField("lineTotal" + i).value) || 0;
         subtotal += lineValue;
       }
     }
     this.getField("subtotal").value = subtotal.toFixed(2);
     
     // Calculate discount
     var discountType = this.getField("discountType").value;
     var discountValue = parseFloat(this.getField("discountValue").value) || 0;
     var discountAmount = 0;
     
     if (discountType === "Percentage") {
       discountAmount = subtotal * (discountValue / 100);
     } else if (discountType === "Fixed Amount") {
       discountAmount = discountValue;
     }
     
     this.getField("discountAmount").value = discountAmount.toFixed(2);
     
     // Calculate taxable amount
     var taxableAmount = subtotal - discountAmount;
     this.getField("taxableAmount").value = taxableAmount.toFixed(2);
     
     // Calculate tax
     var taxRate = parseFloat(this.getField("taxRate").value) || 0;
     var taxAmount = taxableAmount * (taxRate / 100);
     this.getField("taxAmount").value = taxAmount.toFixed(2);
     
     // Calculate shipping
     var shippingCost = parseFloat(this.getField("shippingCost").value) || 0;
     
     // Calculate grand total
     var grandTotal = taxableAmount + taxAmount + shippingCost;
     this.getField("grandTotal").value = grandTotal.toFixed(2);
     
     // Update amount due
     var prepaidAmount = parseFloat(this.getField("prepaidAmount").value) || 0;
     var amountDue = grandTotal - prepaidAmount;
     this.getField("amountDue").value = amountDue.toFixed(2);
   }
   ```

3. **Payment Information Section**:
   - Payment method selection
   - Due date calculation and display
   - Payment instructions
   - Late payment terms
   - Partial payment handling

## Using [RevisePDF](https://www.revisepdf.com) for Self-Calculating Forms

Creating professional forms without specialized software:

### Creating Invoice Templates Online

1. **Getting Started with [RevisePDF](https://www.revisepdf.com)**:
   - Visit [RevisePDF.com](https://www.revisepdf.com)
   - Select invoice template or start from scratch
   - Configure basic document settings
   - Add company information and branding
   - Set up customer information fields

2. **Setting Up Calculation Fields**:
   - Add line item table structure
   - Configure quantity and price fields
   - Set up line total calculations
   - Create subtotal and summary sections
   - Implement tax and discount calculations

3. **Advantages of [RevisePDF](https://www.revisepdf.com)**:
   - No software installation required
   - Works on any device with a web browser
   - Pre-built calculation templates
   - Real-time calculation testing
   - Professional design options

### Template Customization and Branding

1. **Visual Customization Options**:
   - Add company logo and branding
   - Customize colors and typography
   - Adjust layout and spacing
   - Create professional header and footer
   - Add terms and payment instructions

2. **Field Customization**:
   - Rename fields for your business needs
   - Add industry-specific fields
   - Customize calculation formulas
   - Set appropriate field formats
   - Configure field validation

3. **Creating Reusable Templates**:
   - Save custom templates for future use
   - Create variations for different purposes
   - Implement consistent branding
   - Share templates with team members
   - Update templates as needed

### Distribution and Usage

1. **Sharing Options**:
   - Email forms directly to clients
   - Generate shareable links
   - Download for offline use
   - Embed in websites or portals
   - Print for physical distribution

2. **Data Collection Methods**:
   - Email submission
   - Online form submission
   - Centralized data collection
   - Integration with other systems
   - Offline completion and return

3. **Processing Completed Forms**:
   - Review submitted invoices
   - Export data to accounting systems
   - Generate reports and analytics
   - Track payment status
   - Archive completed documents

## Best Practices for Self-Calculating Forms

Guidelines for effective, professional documents:

### Design and Usability

1. **Clear Visual Hierarchy**:
   - Emphasize important totals and amounts
   - Create distinct sections with visual separation
   - Use consistent styling for similar elements
   - Implement appropriate typography
   - Balance white space and content

2. **User-Friendly Data Entry**:
   - Provide clear field labels
   - Implement logical tab order
   - Add helpful tooltips and instructions
   - Use appropriate field types
   - Consider mobile and touch users

3. **Professional Appearance**:
   - Create consistent branding
   - Use appropriate color schemes
   - Implement clean, organized layouts
   - Ensure proper alignment and spacing
   - Design for both screen and print

### Calculation Reliability

1. **Robust Formula Implementation**:
   - Handle empty fields gracefully
   - Prevent division by zero errors
   - Implement proper rounding rules
   - Validate inputs before calculation
   - Test with extreme values

2. **Calculation Order Management**:
   - Ensure proper sequence of operations
   - Handle dependent calculations correctly
   - Prevent circular references
   - Document calculation dependencies
   - Test calculation chain thoroughly

3. **Error Prevention and Handling**:
   - Validate inputs before processing
   - Provide clear error messages
   - Implement range checking
   - Handle special cases appropriately
   - Test edge cases thoroughly

### Testing and Verification

1. **Comprehensive Testing Strategy**:
   - Test with various input combinations
   - Verify all calculations manually
   - Check boundary conditions
   - Test with different PDF readers
   - Verify printing behavior

2. **Common Scenarios to Test**:
   - Zero quantity or amount entries
   - Maximum expected values
   - Fractional quantities
   - Discount and tax interactions
   - Multiple line items with varied values

3. **User Testing**:
   - Have actual users complete sample forms
   - Gather feedback on usability
   - Identify confusion points
   - Test with different devices
   - Refine based on user experience

## Conclusion

Self-calculating PDF invoices and order forms represent one of the most valuable applications of interactive PDF technology. By implementing automatic calculations, you eliminate errors, save time, and create a more professional experience for both your business and your customers.

Whether you're creating simple order forms or sophisticated invoices with complex pricing structures, the principles and techniques outlined in this guide will help you develop effective, reliable self-calculating documents. Remember that the most successful forms balance technical functionality with clear design and excellent usability.

Tools like [RevisePDF](https://www.revisepdf.com) make it easier than ever to create professional self-calculating forms without specialized software, allowing you to implement sophisticated calculations and create branded templates from any device with a web browser.

---

*Need to create professional self-calculating invoices and order forms without specialized software? Visit [RevisePDF.com](https://www.revisepdf.com) for easy-to-use tools that help you design, build, and implement automatic calculations from any device with a web browser.*
