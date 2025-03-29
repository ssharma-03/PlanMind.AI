import os
from dotenv import load_dotenv
import json
import time

# Load environment variables
load_dotenv()

# Optional IBM Watson import - will try first but fall back to OpenAI if not available
try:
    from ibm_watson_machine_learning import APIClient
    IBM_AVAILABLE = True
except ImportError:
    IBM_AVAILABLE = False
    print("IBM Watson Machine Learning package not available. Using OpenAI fallback.")

# Optional OpenAI import for fallback
try:
    import openai
    OPENAI_AVAILABLE = True
    openai.api_key = os.getenv("OPENAI_API_KEY")
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI package not available.")

def get_watson_client():
    """Initialize and return IBM Watson client if available"""
    if not IBM_AVAILABLE:
        return None
        
    try:
        # IBM Watson credentials
        wml_credentials = {
            "apikey": os.getenv("IBM_API_KEY"),
            "url": os.getenv("IBM_URL")
        }
        client = APIClient(wml_credentials)
        return client
    except Exception as e:
        print(f"Error initializing Watson client: {e}")
        return None

def generate_strategy_with_watson(business_problem, context=""):
    """Generate strategic approaches using IBM WatsonX"""
    client = get_watson_client()
    if not client:
        return None
    
    try:
        # Set up IBM Watson
        space_id = os.getenv("IBM_SPACE_ID")
        client.set.default_space(space_id)
        
        # Construct the prompt
        prompt = construct_prompt(business_problem, context)
        
        # Set up parameters for text generation
        model_id = "ibm/granite-13b-instruct-v2"  # Use appropriate model ID
        
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": 2048,
            "min_new_tokens": 100,
            "temperature": 0.7,
            "top_k": 50,
            "top_p": 1
        }
        
        # Generate text
        response = client.text_generation.create(
            model_id=model_id,
            prompt=prompt,
            parameters=parameters
        )
        
        # Extract the generated text
        generated_text = response.get("results", [{}])[0].get("generated_text", "")
        
        if not generated_text:
            return None
            
        return generated_text
    
    except Exception as e:
        print(f"Error generating strategy with Watson: {e}")
        return None

def generate_strategy_with_openai(business_problem, context=""):
    """Generate strategic approaches using OpenAI as fallback"""
    if not OPENAI_AVAILABLE:
        return None
    
    try:
        # Construct the prompt
        prompt = construct_prompt(business_problem, context)
        
        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a highly experienced Business Strategy Consultant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"Error generating strategy with OpenAI: {e}")
        return None

def construct_prompt(business_problem, context=""):
    """Construct the prompt for AI services"""
    return f"""You are acting as a highly experienced Business Strategy Consultant.

Your task is to help businesses create actionable and optimized strategic plans based on the following input problem.

Problem:
{business_problem}

Additional Context:
{context}

Please perform the following:

1. Generate 3 different strategic approaches to solve this problem.
   - Name each strategy uniquely.
   - Describe each strategy briefly.
   
2. For each strategy, provide:
   - Estimated resource allocation (people, budget, tools, timeline)
   - Major steps involved
   
3. Identify possible risks & limitations for each strategy.
   - For each risk, suggest a mitigation plan.

4. Recommend additional tips, tools, or AI-powered enhancements that can further optimize the chosen strategy.

Make sure the output is:
- Structured
- Easy to understand
- Suitable for non-technical business users
- Professional and business-friendly
"""

def generate_strategy(business_problem, context=""):
    """
    Generate strategic approaches using available AI services
    Tries IBM Watson first, falls back to OpenAI, then to a hardcoded response
    """
    # Try IBM Watson first (if available)
    if IBM_AVAILABLE:
        response = generate_strategy_with_watson(business_problem, context)
        if response:
            return response
    
    # Fall back to OpenAI (if available)
    if OPENAI_AVAILABLE:
        response = generate_strategy_with_openai(business_problem, context)
        if response:
            return response
    
    # If all else fails, return a hardcoded response
    print("Using fallback hardcoded response as no AI services are available")
    return generate_fallback_response(business_problem, context)

def generate_fallback_response(business_problem, context=""):
    """Fallback hardcoded response when no AI services are available"""
    return f"""# Strategic Approaches for Your Business Problem

## Strategy 1: Digital Transformation Initiative
**Description**: Leverage digital technologies to streamline operations and enhance customer experience.

**Resource Allocation**:
- **People**: 3-5 IT specialists, 1 project manager, department representatives
- **Budget**: $50,000-$100,000 depending on scope
- **Tools**: CRM system, automation software, analytics platform
- **Timeline**: 6-8 months

**Major Steps**:
1. Conduct digital readiness assessment
2. Identify high-impact processes for digitization
3. Select and implement appropriate technologies
4. Train staff on new systems
5. Measure results and optimize

**Risks & Limitations**:
- **Risk**: Employee resistance to new technologies
  - **Mitigation**: Comprehensive training program and change management
- **Risk**: Technical implementation challenges
  - **Mitigation**: Start with pilot projects before full rollout
- **Risk**: Budget overruns
  - **Mitigation**: Phased approach with clear ROI metrics for each phase

## Strategy 2: Customer-Centric Restructuring
**Description**: Reorganize business processes around customer journey and experiences.

**Resource Allocation**:
- **People**: External consultant, customer experience team (3-4 people)
- **Budget**: $30,000-$60,000
- **Tools**: Customer journey mapping software, feedback collection tools
- **Timeline**: 3-5 months

**Major Steps**:
1. Map current customer journeys and identify pain points
2. Collect and analyze customer feedback
3. Redesign processes to eliminate friction points
4. Implement changes in customer-facing departments
5. Establish ongoing feedback mechanisms

**Risks & Limitations**:
- **Risk**: Misidentifying customer priorities
  - **Mitigation**: Data-driven approach using multiple feedback channels
- **Risk**: Internal resistance to change
  - **Mitigation**: Create cross-functional teams to drive buy-in
- **Risk**: Short-term disruption to service
  - **Mitigation**: Implement changes gradually with careful monitoring

## Strategy 3: Strategic Partnerships Expansion
**Description**: Form partnerships with complementary businesses to expand offerings and reach.

**Resource Allocation**:
- **People**: Business development lead, legal advisor, operations coordinator
- **Budget**: $20,000-$40,000 (excluding partnership investments)
- **Tools**: CRM, collaboration tools, legal contract management
- **Timeline**: 4-6 months for initial partnerships

**Major Steps**:
1. Identify partnership gaps and opportunities
2. Research and shortlist potential partners
3. Develop partnership proposals and approach candidates
4. Negotiate terms and formalize agreements
5. Launch joint initiatives

**Risks & Limitations**:
- **Risk**: Partner misalignment on goals or values
  - **Mitigation**: Thorough vetting process and clear agreement terms
- **Risk**: Dependency on external entities
  - **Mitigation**: Diversify partnerships and maintain core competencies
- **Risk**: Brand dilution
  - **Mitigation**: Establish clear brand guidelines for partnership activities

## Additional Optimization Recommendations

- Implement AI-powered analytics to continuously monitor strategy performance
- Consider a hybrid approach combining elements from multiple strategies
- Establish a digital dashboard for real-time tracking of key metrics
- Use scenario planning tools to prepare for potential market shifts
""" 