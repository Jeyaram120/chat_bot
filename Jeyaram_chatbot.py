import json
import re
from datetime import datetime

# --- Part 1: Dummy Tools ---
class Tool:
    def __init__(self, name, description):
        self.name = name
        self.description = description

    def execute(self, **kwargs):
        raise NotImplementedError("Subclasses must implement this method.")


class OrderDBTool(Tool):
    def __init__(self):
        super().__init__(
            name="OrderDBTool",
            description="Use this tool to get information about a customer's order status. Requires 'order_id'."
        )
        self.dummy_orders = {
            "ORD123": {"status": "Shipped", "estimated_delivery": "2025-05-15"},
            "ORD456": {"status": "Processing", "estimated_delivery": "2025-05-18"},
            "ORD789": {"status": "Delivered", "delivery_date": "2025-05-10"},
            "ORD741": {"status": "Delivered", "delivery_date": "2025-05-10"},
        }

    def execute(self, order_id: str = None):
        if not order_id:
            return json.dumps({"error": "Order ID is required."}) # Empty input
        

        order_id = order_id.strip().upper() # Case-insensitive 
        
        if order_id in self.dummy_orders:
            return json.dumps(self.dummy_orders[order_id]) # Exact match
        else:
            return json.dumps({"error": f"Order {order_id} not found in our system."}) # No match at all

# json.dumps() ----> It Converts a Python object (Dictionary) into a JSON-formatted string
# f"...."" ---> To embed expressions or variables directly inside a string using {}.

class ProductInfoTool(Tool):
    def __init__(self):
        super().__init__(
            name="ProductInfoTool",
            description="Use this tool to get information about a product. Requires 'product_name'."
        )
        self.dummy_products = {
            "laptop": {"description": "A high-performance laptop.", "price": "$1200", "in_stock": True},
            "mouse": {"description": "An ergonomic wireless mouse.", "price": "$25", "in_stock": False},
            "keyboard": {"description": "A mechanical gaming keyboard.", "price": "$75", "in_stock": True},
        }

    def execute(self, product_name: str = None):
        if not product_name:
            return json.dumps({"error": "Product name is required."}) # Empty input
        
        product_name_lower = product_name.lower().strip() # Case-insensitive 
        
        if product_name_lower in self.dummy_products:
            return json.dumps(self.dummy_products[product_name_lower]) # Exact match
        else:

            for product in self.dummy_products.keys():
                if product in product_name_lower or product_name_lower in product:
                    return json.dumps(self.dummy_products[product]) # Partial match Eg: "keyboard" is in "gaming keyboard" or "gamingkeyboard"
            
            return json.dumps({"error": f"Product '{product_name}' not found in our catalog."}) # No match at all


class PolicyTool(Tool):
    def __init__(self):
        super().__init__(
            name="PolicyTool",
            description="Use this tool to get information about company policies, like 'return policy' or 'shipping policy'."
        )
        self.dummy_policies = {
            "return policy": "You can return items within 30 days of purchase for a full refund, provided they are in original condition.",
            "shipping policy": "Standard shipping takes 3-5 business days. Express shipping is available for an additional cost.",
        }

    def execute(self, policy_type: str = None):
        if not policy_type:
            return json.dumps({"error": "Policy type is required."}) # Empty input
        
        policy_type_lower = policy_type.lower().strip() # Case-insensitive 
        
        if policy_type_lower in self.dummy_policies:
            return json.dumps({"policy": policy_type_lower, "details": self.dummy_policies[policy_type_lower]}) # Exact match
        else:

            for policy in self.dummy_policies.keys():
                if policy in policy_type_lower or any(word in policy for word in policy_type_lower.split()):
                    return json.dumps({"policy": policy, "details": self.dummy_policies[policy]}) # Partial match with keys
            
            available_policies = list(self.dummy_policies.keys())
            return json.dumps({"error": f"Policy type '{policy_type}' not found. Available policies: {available_policies}"}) # No match at all


class OrderIssuesTool(Tool):
    def __init__(self):
        super().__init__(
            name="OrderIssuesTool",
            description="Use this tool to handle order-related complaints and issues like non-delivery, damaged items, wrong items, etc. Requires 'order_id' and 'issue_type'."
        )
        self.dummy_orders = {
            "ORD123": {"status": "Shipped", "estimated_delivery": "2025-05-15"},
            "ORD456": {"status": "Processing", "estimated_delivery": "2025-05-18"},
            "ORD789": {"status": "Delivered", "delivery_date": "2025-05-10"},
        }
        
        self.issue_resolutions = {
            "not_received": {
                "action": "investigation",
                "message": "I understand you haven't received your order yet. I'm initiating an investigation with our shipping partner. We'll track your package and provide an update within 24 hours. If not located, we'll process a replacement or full refund immediately.",
                "next_steps": ["Track package with carrier", "Contact shipping partner", "Issue replacement/refund if needed"],
                "escalation": True
            },
            "damaged": {
                "action": "replacement",
                "message": "I'm sorry your item arrived damaged. We'll send a replacement immediately at no cost. Please keep the damaged item until the replacement arrives, then we'll arrange pickup of the damaged product.",
                "next_steps": ["Process replacement order", "Schedule pickup of damaged item", "Expedite shipping"],
                "escalation": False
            },
            "wrong_item": {
                "action": "exchange",
                "message": "I apologize for sending the wrong item. We'll send the correct product right away and arrange pickup of the incorrect item. You won't be charged for return shipping.",
                "next_steps": ["Process correct order", "Schedule pickup", "Verify correct item details"],
                "escalation": False
            },
            "defective": {
                "action": "replacement_or_refund",
                "message": "I'm sorry the product is defective. We can either send a replacement or process a full refund. Which would you prefer? We'll also arrange pickup of the defective item.",
                "next_steps": ["Offer replacement or refund choice", "Process selected option", "Arrange pickup"],
                "escalation": False
            },
            "late_delivery": {
                "action": "investigation",
                "message": "I understand your order is late. Let me check the current status and estimated delivery time. We'll also look into compensation for the delay.",
                "next_steps": ["Check delivery status", "Contact carrier", "Offer compensation"],
                "escalation": True
            }
        }

    def classify_issue(self, description: str) -> str: # -> str means It Returns a string
        description_lower = description.lower() # Case-insensitive 

        # intent matching with issue_resolutions keys
        if any(word in description_lower for word in ["not received", "didn't receive", "haven't got", "missing", "lost"]): 
            return "not_received"
        elif any(word in description_lower for word in ["damaged", "broken", "cracked", "smashed"]):
            return "damaged"
        elif any(word in description_lower for word in ["wrong", "incorrect", "different", "not what i ordered"]):
            return "wrong_item"
        elif any(word in description_lower for word in ["defective", "not working", "faulty", "doesn't work", "broken"]):
            return "defective"
        elif any(word in description_lower for word in ["late", "delayed", "slow", "taking too long"]):
            return "late_delivery"
        else:
            return "general_issue"

    def execute(self, order_id: str = None, issue_type: str = None, description: str = None):
        if not order_id:
            return json.dumps({"error": "Order ID is required to handle the issue."}) # Empty input
        
        order_id = order_id.strip().upper() # Case-insensitive 
        
        if order_id not in self.dummy_orders:
            return json.dumps({"error": f"Order {order_id} not found in our system."}) #Invalid or Unknown Order ID Error Handling
        

        if not issue_type and description:
            issue_type = self.classify_issue(description) # Calling classify_issue method to select the issue_resolutions
        elif not issue_type:
            return json.dumps({"error": "Please describe the issue you're experiencing with your order."}) # No Match issue description found
        

        resolution = self.issue_resolutions.get(issue_type, {
            "action": "escalation",
            "message": "I understand you're having an issue with your order. Let me escalate this to our specialized support team who will contact you within 2 hours to resolve this matter.",
            "next_steps": ["Escalate to specialized support", "Schedule callback within 2 hours"],
            "escalation": True
        })
        # self.issue_resolutions.get(issue_type, {}) -----> Syntax: dictionary.get(key, default_value). 
        # It means If the issue_type is not found at the issue_resolutions dictionary then it use the Default dictionary

        response = {
            "order_id": order_id,
            "issue_type": issue_type,
            "resolution": resolution["action"],
            "message": resolution["message"],
            "next_steps": resolution["next_steps"],
            "escalated": resolution["escalation"],
            "ticket_created": True,
            "ticket_id": f"TICKET-{order_id}-{hash(str(issue_type)) % 10000:04d}"
        }
        # hash(str(issue_type))
        # str() ----> Converts the issue_type to a string (Optional)
        # hash() ----> Python’s built-in hash() function to get a numeric hash Eg: 2538627051216319900
        # % 10000:04d -----> keeps only the last 4 digits of the hash to make the ID short Eg: 9900
        # :04d f-string format specifier 0 mean pad with leading zero (Optional), 4 means 4 digits and d means treat the value as a decimal (integer)

        # Eg: f"TICKET-{order_id}-{hash(str(issue_type)) % 10000:04d}" ---> TICKET-ORD123-9900

        return json.dumps(response)


class GeneralInquiryTool(Tool):
    def __init__(self):
        super().__init__(
            name="GeneralInquiryTool",
            description="Use this tool for general customer inquiries, complaints, feedback, or questions that don't fit other categories."
        )
        
        self.inquiry_responses = {
            "complaint": {
                "message": "I sincerely apologize for your negative experience. Your feedback is very important to us and helps us improve our service. I'd like to escalate this to our customer experience team to ensure we address your concerns properly.",
                "action": "escalate_to_customer_experience"
            },
            "feedback": {
                "message": "Thank you for taking the time to share your feedback! We truly value customer input as it helps us improve our products and services. I'll make sure your feedback reaches the appropriate team.",
                "action": "forward_to_feedback_team"
            },
            "general_question": {
                "message": "I'd be happy to help with your question. Could you please provide more specific details about what you'd like to know?",
                "action": "request_clarification"
            },
            "business_hours": {
                "message": "Our customer support is available 24/7 through this chat. Our phone support is available Monday-Friday 9AM-6PM EST, and Saturday-Sunday 10AM-4PM EST.",
                "action": "provide_information"
            },
            "contact_info": {
                "message": "You can reach us through: \n• This chat (24/7)\n• Phone: 1-800-SUPPORT\n• Email: support@ecommerce.com\n• Social media: @ecommercesupport",
                "action": "provide_information"
            }
        }

    def classify_inquiry(self, text: str) -> str: # -> str means It Returns a string
        text_lower = text.lower()  # Case-insensitive 
        
        # intent matching with inquiry_responses keys
        if any(word in text_lower for word in ["complain", "disappointed", "terrible", "awful", "bad experience", "unhappy"]):
            return "complaint"
        elif any(word in text_lower for word in ["feedback", "suggestion", "improve", "better"]):
            return "feedback"
        elif any(word in text_lower for word in ["hours", "open", "available", "when"]):
            return "business_hours"
        elif any(word in text_lower for word in ["contact", "phone", "email", "reach"]):
            return "contact_info"
        else:
            return "general_question"

    def execute(self, inquiry_type: str = None, message: str = None):
        if not message:
            return json.dumps({"error": "Please provide details about your inquiry."}) # Empty input
        
        if not inquiry_type:
            inquiry_type = self.classify_inquiry(message) # Calling classify_inquiry method to select the inquiry_responses
        
        response_data = self.inquiry_responses.get(inquiry_type, self.inquiry_responses["general_question"])
        
        # self.inquiry_responses.get(inquiry_type, {}) -----> Syntax: dictionary.get(key, default_value). 
        # It means If the inquiry_type is not found at the inquiry_responses dictionary then it use the Default dictionary "general_question"

        result = {
            "inquiry_type": inquiry_type,
            "message": response_data["message"],
            "action": response_data["action"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "follow_up_needed": inquiry_type in ["complaint", "general_question"]
        }
        # datetime.now() ---> To get the current local date and time.
        # .strftime("%Y-%m-%d %H:%M:%S") ----> 4-digit year | 2-digit month | 2-digit day | 2-digit hour (24-hour clock) | 2-digit minute | 2-digit second

        return json.dumps(result)

# --- Part 2: Mock LLM Call ---
def mock_llm_call(prompt_type: str, data: str = None, query: str = None, tool_description: str = None) -> str:
    # Getting Parameter for mock_llm_call () : prompt_type, data[None], query[None], tool_description[None]

    if prompt_type == "formulate_response_with_data" and data: # Check prompt_type == "formulate_response_with_data" and data is not Empty
        try:
            parsed_data = json.loads(data) # Load the JSON data back JSON Objects --to--> Python Dictionaries
            # print(parsed_data)

            if "error" in parsed_data:
                return f"I'm sorry, but {parsed_data['error']} Please double-check the information and try again."
            
            # If status is in (or) present at the parsed_data then continue the execution inside the if 
            # and return the response as a Bot Message to the User
            if "status" in parsed_data: 
                response = f"Here's your order information:\n"
                response += f"• Status: {parsed_data['status']}\n"
                if "estimated_delivery" in parsed_data:
                    response += f"• Estimated Delivery: {parsed_data['estimated_delivery']}"
                elif "delivery_date" in parsed_data:
                    response += f"• Delivered on: {parsed_data['delivery_date']}"
                return response
                
            # If description is in (or) present at the parsed_data    
            elif "description" in parsed_data:  
                response = f"Product Information:\n"
                response += f"• Description: {parsed_data['description']}\n"
                response += f"• Price: {parsed_data['price']}\n"
                response += f"• In Stock: {'Yes' if parsed_data.get('in_stock', False) else 'No'}"
                return response
                
            # If policy is in (or) present at the parsed_data    
            elif "policy" in parsed_data:  
                return f"Here's our {parsed_data['policy']}:\n\n{parsed_data['details']}"
            
            # If stresolution is in (or) present at the parsed_data
            elif "resolution" in parsed_data:
                response = f"I understand your concern about order {parsed_data['order_id']}.\n\n"
                response += f"{parsed_data['message']}\n\n"
                response += "Next steps:\n"
                for i, step in enumerate(parsed_data['next_steps'], 1):
                    response += f"{i}. {step}\n"
                response += f"\nTicket ID: {parsed_data['ticket_id']}"
                if parsed_data.get('escalated'):
                    response += "\n⚠️ This issue has been escalated for priority handling."
                return response
            
            # If inquiry_type is in (or) present at the parsed_data
            elif "inquiry_type" in parsed_data:  
                response = parsed_data['message']
                if parsed_data.get('follow_up_needed'):
                    response += "\n\nIs there anything else I can help you with regarding this matter?"
                return response
            
            # If the If and all the elif are false or fail then the else will execute
            else:
                formatted_data = json.dumps(parsed_data, indent=2)
                return f"Here's the information I found:\n{formatted_data}"

        # if any error occurred while the try sections json.loads() and other executed then executed the exception return
        except json.JSONDecodeError:
            return f"Here's the information: {data}"
    
    elif prompt_type == "formulate_response_no_data": # Check prompt_type == "formulate_response_with_data"
        return ("I'm sorry, I couldn't find the specific information you're looking for with my current tools. "
                "I can help you with order status, product information, or company policies. "
                "Could you please rephrase your question or provide more specific details?")
    
    elif prompt_type == "clarification": # Check prompt_type == "clarification"
        clarification_messages = {
            "order": "To check your order status, I'll need your order ID (like ORD123). Could you please provide it?",
            "product": "I'd be happy to help with product information! Which specific product are you interested in? (laptop, mouse, keyboard)",
            "policy": "I can help with our policies! Which policy would you like to know about? (return policy, shipping policy)"
        }
        

        if query:
            query_lower = query.lower() # Case-insensitive 
            if "order" in query_lower: 
                return clarification_messages["order"] # if "order" in query_lower
            elif "product" in query_lower:
                return clarification_messages["product"] # if "product" in query_lower
            elif "policy" in query_lower:
                return clarification_messages["policy"] # if "policy" in query_lower
        
        # If query is Empty(None) or False
        return ("I need a bit more information to help you effectively. "
                "Please provide more details about what you're looking for - "
                "an order ID, product name, or specific policy type.")
    
    elif prompt_type == "choose_tool_reasoning": # Check prompt_type == "choose_tool_reasoning"

        print(f"--- LLM Reasoning (Simulated) ---")
        print(f"User query: {query}")
        print(f"Available tools: {tool_description}")
        print(f"Analyzing query for keywords and intent...")
        print(f"--- End LLM Reasoning ---")
        return "Reasoning logged."
    
    # If the If and all the elif are false or fail then the else will execute
    else:
        return "I'm not sure how to respond to that. Could you please rephrase your question?"


# --- Part 3: Agent Class ---
class Agent:
    def __init__(self, tools: list): # tools: list means list of tool objects Eg: [OrderDBTool(), ProductInfoTool()]
        self.tools = {tool.name: tool for tool in tools} # It constructs a dictionary from the provided tools list with tool name and tool instance.
        self.tool_descriptions_for_llm = "\n".join([f"- {tool.name}: {tool.description}" for tool in tools]) # join() A single string with all elements joined by \n.

    def extract_order_id(self, text: str) -> str:
        
        # r means to treate the Backslashes (\) as a raw string literal not as an escape characters or sequence
        patterns = [
            r'\b(ORD\d+)\b',                    # It Matches strings starting with "ORD" followed by one or more digits (\d+) Eg: ORD123
            r'\border\s*#?\s*(\w+)\b',          # It Matches the word "order" followed optionally by a #, then captures the next sequence of alphanumeric characters. Eg: order ORD123
            r'\b#(\w+)\b',                      # It Matches a # followed by one or more alphanumeric characters Eg: #ORD123
            r'\b([A-Z]{3}\d+)\b'                # It Matches any three uppercase letters followed by one or more digits Eg: Any 3 letters + digits
        ]
        
        text_upper = text.upper() # Case-insensitive 
        for pattern in patterns:
            matches = re.findall(pattern, text_upper, re.IGNORECASE) # check any pattern matches to text_upper without case-sensitive using re python built-in module 
            if matches:
                order_id = matches[0]

                if not order_id.startswith('ORD') and order_id.isdigit(): # If order_id not start with ORD and has no digits or number then continue the iteration
                    continue 
                return order_id # Otherwise return the order_id and exit from the iteration
        
        return None # If Nothing Matches to the Patterns then return None

    def extract_product_name(self, text: str) -> str:
        text_lower = text.lower() # Case-insensitive 
        

        products = ["laptop", "mouse", "keyboard"]
        

        for product in products:
            if product in text_lower:
                return product  # check any products matches to text_lower if it then return the product
        

        product_indicators = ["about", "price", "cost", "buy", "purchase", "info", "information"]
        words = text_lower.split() # spliting the text_lower into a splited words list
        
        for i, word in enumerate(words): # enumerate(words) will iterate words list from the default starting index 0
            if word in product_indicators and i + 1 < len(words):
                potential_product = words[i + 1] # it check with the word list next index since the product name may come after the product_indicators Eg: ['Inormation', 'about', 'laptop']
                if potential_product in products:
                    return potential_product # if any potential_product found it returns it
        
        return None # Otherwise return None

    def extract_order_issue_info(self, text: str) -> dict:
        result = {"order_id": None, "description": text}
        

        order_id = self.extract_order_id(text) # Calling extract_order_id() to Extract the Order ID from the text or description
        if order_id:
            result["order_id"] = order_id # if the extract_order_id() does not return None and return the order_id then assign it to the result["order_id"]
        
        return result

    def is_order_complaint(self, text: str) -> bool:
        text_lower = text.lower() # Case-insensitive 
        

        complaint_words = ["not received", "didn't receive", "haven't got", "missing", "damaged", 
                          "broken", "wrong", "incorrect", "defective", "not working", "late", 
                          "delayed", "problem", "issue", "complaint"]
        
        order_indicators = ["order", "ordered", "purchase", "bought", "delivery", "package"]
        
        has_complaint = any(word in text_lower for word in complaint_words) # Check any of text_lower word exists in the complaint_words iteratively if yes then true otherwise false
        has_order_context = any(word in text_lower for word in order_indicators) # Check any of text_lower word exists in the order_indicators iteratively if yes then true otherwise false
        
        return has_complaint and has_order_context # It return True only if both has_complaint and has_order_context are TRUE

    def is_general_inquiry(self, text: str) -> bool:

        text_lower = text.lower() # Case-insensitive 
        
        inquiry_indicators = ["help", "question", "how", "what", "when", "where", "why", 
                             "complain", "feedback", "suggestion", "contact", "hours"]
        
        return any(word in text_lower for word in inquiry_indicators) # Check any of text_lower word exists in the inquiry_indicators iteratively if yes then return true otherwise false

    def extract_policy_type(self, text: str) -> str:

        text_lower = text.lower() # Case-insensitive 
        
        if "return" in text_lower: # Check for return in text_lower
            return "return policy"
        elif "shipping" in text_lower or "delivery" in text_lower: # Check for shipping or delivery in text_lower
            return "shipping policy"
        elif "policy" in text_lower: # Check for policy in text_lower
            if any(word in text_lower for word in ["back", "refund", "exchange"]): # Check any of text_lower word exists in the ["back", "refund", "exchange"] iteratively if yes then true otherwise false
                return "return policy"
            elif any(word in text_lower for word in ["ship", "deliver", "send"]): # Check any of text_lower word exists in the ["ship", "deliver", "send"] iteratively if yes then true otherwise false
                return "shipping policy"
        
        return None # Nothing Satisfied then return None

    def choose_tool(self, query: str):
        
        # Calling mock_llm_call()
        mock_llm_call(prompt_type="choose_tool_reasoning", query=query, tool_description=self.tool_descriptions_for_llm)
        
        query_lower = query.lower() # Case-insensitive 
        chosen_tool = None
        params = {} 

        if self.is_order_complaint(query): # If is_order_complaint() return True for the Passed Query then the inside if statement will executed
            issue_info = self.extract_order_issue_info(query) # It extract_order_issue_info() assign the Dict {"order_id": Value, "description": query} to the issue_info variable
            if issue_info["order_id"]: # If issue_info["order_id"] is not None
                params["order_id"] = issue_info["order_id"] # Assign params["order_id"] as issue_info["order_id"]
                params["description"] = issue_info["description"] # Assign params["description"] as issue_info["description"]
                chosen_tool = self.tools.get("OrderIssuesTool") # It looks up the OrderIssuesTool instance in the self.tools dictionary
            else:
                chosen_tool = self.tools.get("OrderIssuesTool") # It looks up the OrderIssuesTool instance in the self.tools dictionary
                params["description"] = query # Assign params["description"] as query
        
        # if self.is_order_complaint(query) return False then if the chosen_tool is None and query_lower keyword in ["order", "status", "tracking", "delivery", "shipped", "delivered"] then execute this statement
        elif not chosen_tool and any(keyword in query_lower for keyword in ["order", "status", "tracking", "delivery", "shipped", "delivered"]):
            order_id = self.extract_order_id(query) # It extract_order_id() assign the string order_id to the order_id variable
            if order_id: # order_id is not None
                params["order_id"] = order_id # Assign params["order_id"] as order_id
                chosen_tool = self.tools.get("OrderDBTool") # It looks up the OrderDBTool instance in the self.tools dictionary
            else:
                chosen_tool = self.tools.get("OrderDBTool") # It looks up the OrderDBTool instance in the self.tools dictionary
        
        # If still the chosen_tool is None and query_lower keyword in ["product", "price", "cost", "buy", "purchase", "laptop", "mouse", "keyboard", "tell me about", "how much"] then execute this statement
        elif not chosen_tool and any(keyword in query_lower for keyword in ["product", "price", "cost", "buy", "purchase", "laptop", "mouse", "keyboard", "tell me about", "how much"]):
            product_name = self.extract_product_name(query) # It extract_product_name() assign the string product to the product_name variable
            if product_name: # product_name is not None
                params["product_name"] = product_name # Assign params["product_name"] as product_name
                chosen_tool = self.tools.get("ProductInfoTool") # It looks up the ProductInfoTool instance in the self.tools dictionary
            else:
                chosen_tool = self.tools.get("ProductInfoTool") # It looks up the ProductInfoTool instance in the self.tools dictionary
        
        # If still the chosen_tool is None and query_lower keyword in ["policy", "return", "refund", "shipping", "delivery"] then execute this statement
        elif not chosen_tool and any(keyword in query_lower for keyword in ["policy", "return", "refund", "shipping", "delivery"]):
            policy_type = self.extract_policy_type(query) # It extract_policy_type() assign the string policy name to the policy_type variable
            if policy_type: # policy_type is not None
                params["policy_type"] = policy_type # Assign params["policy_type"] as policy_type
                chosen_tool = self.tools.get("PolicyTool") # It looks up the PolicyTool instance in the self.tools dictionary
            else:
                chosen_tool = self.tools.get("PolicyTool") # It looks up the PolicyTool instance in the self.tools dictionary
        
        # If still the chosen_tool is None and is_general_inquiry() return true then execute this statement
        elif not chosen_tool and self.is_general_inquiry(query):
            params["message"] = query # Assign params["message"] as query
            chosen_tool = self.tools.get("GeneralInquiryTool") # It looks up the GeneralInquiryTool instance in the self.tools dictionary
        
        # If still the chosen_tool is None then execute this statement
        elif not chosen_tool:
            product_name = self.extract_product_name(query) # It extract_product_name() assign the string product to the product_name variable
            if product_name:
                params["product_name"] = product_name # Assign params["product_name"] as product_name
                chosen_tool = self.tools.get("ProductInfoTool") # It looks up the ProductInfoTool instance in the self.tools dictionary
            else:
                params["message"] = query # Assign params["message"] as query
                chosen_tool = self.tools.get("GeneralInquiryTool") # It looks up the GeneralInquiryTool instance in the self.tools dictionary
        
        return chosen_tool, params

    def process_query(self, query: str) -> str:

        chosen_tool, params = self.choose_tool(query) # It choose_tool() execute and return chosen_tool, params to the variable chosen_tool, params
        
        if chosen_tool: # chosen_tool is Not None
            print(f"[Agent Log] Chosen tool: {chosen_tool.name} with params: {params}") # print the chosen_tool name and params

            if chosen_tool.name == "OrderIssuesTool" and not params.get("order_id"): # If chosen_tool is OrderIssuesTool and not has params[order_id] then return its following statement
                return mock_llm_call(prompt_type="clarification", query="To help resolve your order issue, I'll need your order ID (like ORD123). Could you please provide it?")
            

            if chosen_tool.name == "OrderDBTool" and not params.get("order_id"): # If chosen_tool is OrderDBTool and not has params[order_id] then return its following statement
                return mock_llm_call(prompt_type="clarification", query=query)
            

            if chosen_tool.name == "ProductInfoTool" and not params.get("product_name"): # If chosen_tool is ProductInfoTool and not has params[product_name] then return its following statement
                return mock_llm_call(prompt_type="clarification", query=query)
            

            if chosen_tool.name == "PolicyTool" and not params.get("policy_type"): # If chosen_tool is PolicyTool and not has params[policy_type] then return its following statement
                return mock_llm_call(prompt_type="clarification", query=query)

            try:
                tool_output = chosen_tool.execute(**params) # try execute() from tools with params

                response = mock_llm_call(prompt_type="formulate_response_with_data", data=tool_output, query=query) # mock_llm_call() to try formulate_response_with_data
                return response # return the response
            except Exception as e: # if try failed then Execute the Exception Statement
                print(f"[Agent Error] Tool execution failed: {str(e)}")
                return "I encountered an error while processing your request. Please try again or contact support."
        
        else: # chosen_tool is None
            print(f"[Agent Log] No specific tool chosen for the query: '{query}'") # print query

            return mock_llm_call(prompt_type="formulate_response_no_data", query=query) # return mock_llm_call() with formulate_response_with_data

# --- Part 4: Main Interaction Loop ---
if __name__ == "__main__":

     # Creating an instance (object) for each tools
    order_tool = OrderDBTool()
    product_tool = ProductInfoTool()
    policy_tool = PolicyTool()
    order_issues_tool = OrderIssuesTool()
    general_inquiry_tool = GeneralInquiryTool()

    # ordering all availabe tools as list to the variable all_tools
    all_tools = [order_tool, product_tool, policy_tool, order_issues_tool, general_inquiry_tool]


    support_agent = Agent(tools=all_tools) # Passing all available tools to the class Agent

    print("🤖 Welcome to E-commerce Customer Support Bot!")
    print("=" * 60)
    print("I can help you with:")
    print("• Order status & tracking (e.g., 'What is the status of order ORD123?')")
    print("• Order issues & complaints (e.g., 'I ordered ORD123 but didn't receive it')")
    print("• Product information (e.g., 'Tell me about the laptop')")
    print("• Company policies (e.g., 'What is your return policy?')")
    print("• General inquiries & support (e.g., 'I have a complaint about service')")
    print("\nType 'help' for examples or 'exit' to quit.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip() # get input query from the User
            

            if user_input.lower() == 'exit': # if the User Input is exit then print the message and break the while loop
                print("Bot: Thank you for contacting our support! Have a great day! 👋")
                break
            
            if user_input.lower() == 'help': # if the User Input is help then print the message and continue the while loop
                print("\nBot: Here are some example queries you can try:")
                print("📦 Order Status:")
                print("  • 'Check status of order ORD123'")
                print("  • 'Where is my order ORD456?'")
                print("\n⚠️ Order Issues:")
                print("  • 'I ordered ORD789 but didn't receive it'")
                print("  • 'My order ORD123 arrived damaged'")
                print("  • 'Wrong item was delivered for ORD456'")
                print("\n🛍️ Product Information:")
                print("  • 'What is the price of the laptop?'")
                print("  • 'Is the mouse in stock?'")
                print("  • 'Tell me about the keyboard'")
                print("\n📋 Policies:")
                print("  • 'What is your return policy?'")
                print("  • 'What is your shipping policy?'")
                print("\n💬 General Inquiries:")
                print("  • 'I have a complaint about your service'")
                print("  • 'What are your business hours?'")
                print("  • 'How can I contact customer support?'")
                continue
            
            if not user_input:  # if the User Input is none or empty then print the message and continue the while loop
                print("Bot: Please type a question or 'help' for examples.")
                continue


            print("\n[Processing...]")
            agent_response = support_agent.process_query(user_input) # execute process_query() with user input and return back the response to agent_response
            print(f"\nBot: {agent_response}") # print the Bot Message agent_response
            
        except KeyboardInterrupt: # Handles user interruption (e.g., Ctrl+C), prints a message, and exits the loop
            print("\n\nBot: Session interrupted. Goodbye! 👋")
            break
        except Exception as e: # Handles unexpected errors, prints the error message, and suggests contacting support
            print(f"\nBot: I encountered an unexpected error: {str(e)}")
            print("Please try again or contact technical support.")



"""
    In a production-grade implementation, an LLM would leverage advanced NLP techniques to analyze user queries 
    and determine intent with higher precision. This can be achieved using:
    - Embeddings (e.g., OpenAI's GPT, Sentence Transformers) or semantic similarity measures to map queries 
      to tool functionalities, even when user phrasing deviates from predefined patterns.
    - Named Entity Recognition (NER) or dependency parsing to extract structured parameters such as `order_id`, 
      `product_name`, or `policy_type` from unstructured user input.
    - Confidence scores generated through probabilistic models or embeddings, which enable dynamic fallback strategies 
      (e.g., requesting user clarification) or escalating to human support.

    The current approach utilizes static keyword-based matching, which is deterministic and effective for well-defined 
    controlled scenarios but lacks the flexibility to handle ambiguous or multi-intent queries.
"""

"""
    For a fully adaptive response system, an LLM could incorporate additional layers of analysis and contextual adaptation:
    - Sentiment analysis to dynamically adjust response tone based on user emotion (e.g., empathetic for complaints, 
      professional for inquiries).
    - Context management through embeddings or recurrent neural networks to maintain conversational integrity 
      across multi-turn dialogues.
    - Template-driven response generation with dynamic slot filling (e.g., embedding user details or query-specific data 
      into predefined templates) to create more personalized and coherent interactions.

    The current system simulates these functionalities using structured data dictionaries and response templates, 
    which are sufficient for demonstrating basic tool integration but lack scalability for broader conversational needs.
"""

"""
    while dealing with the Structured (MySql) or Unstructured (MongoDB) Database we use the Query or API call at the execute() and through 
    the HTTP or HTTPS request to the hosted Centralized Database and recive the reponse to fetch order statuses, product details, or other relevant information.

    We Can also insert the Booked Complaint ticket to the Database and the support team can make a contact to them 
    regarding the issue in the order order ID, issue type, description, and timestamp... etc
"""
