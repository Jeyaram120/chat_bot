# Chatbot Execution Process

This document outlines the execution flow of a customer service chatbot that handles various user queries related to orders, products, policies, and general support.

---

## 🧩 User Query

The chatbot receives a user query, which may include:

- 🔍 **Order status inquiries**
- 📦 **Product information requests**
- 📜 **Policy-related questions**
- 🛠️ **Complaints or issues with an order**
- 💬 **General inquiries or feedback**

---

## 🧠 Agent Analysis

The chatbot agent analyzes the query to determine its **intent** and selects the appropriate tool:

| Intent                          | Tool Name         | Functionality                                      |
|-------------------------------|-------------------|---------------------------------------------------|
| Order Status                   | `OrderDBTool`     | Retrieves order and delivery details              |
| Product Information            | `ProductInfoTool` | Provides product details, prices, and stock       |
| Return/Shipping Policies       | `PolicyTool`      | Shares return, shipping, and related policies     |
| Order-Related Complaints       | `OrderIssuesTool` | Logs complaints and creates a support ticket      |
| General Questions or Feedback  | `GeneralInquiryTool` | Handles all other inquiries                    |

---

## ⚙️ Tool Execution

Each tool is executed using either:

- **Dummy Data**: For predefined or simulated responses
- **Extracted Parameters**: Such as `order_id`, `product_name`, or `policy_type` from the user's message

---

## 📝 Response Generation

- The result from the selected tool is passed to `mock_llm_call()`  
- This function generates a **natural, human-readable** response for the user

---

## 📤 Response Delivery

The chatbot presents the final response to the user via the chat interface.

---

## 🔁 Continuous Interaction

After responding, the chatbot loops back to await and handle the **next user query**, maintaining a smooth and continuous conversational flow.

---
