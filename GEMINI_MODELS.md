# Gemini Model Overview for ADK

ADK supports several Gemini models with different capabilities and price points. Choosing the right model involves balancing performance, capabilities, and cost for your specific use case.

> **Last Updated:** November 2025  
> **Note:** Gemini 1.5 models are being deprecated. Focus on Gemini 2.5 and 2.0 families for new projects.

## Model Capabilities

| Model | Description | Input Types | Best For |
|-------|-------------|-------------|----------|
| **Gemini 2.5 Pro** | Most powerful model with advanced reasoning and thinking capabilities | Audio, images, video, text | Complex coding, deep reasoning, multimodal understanding |
| **Gemini 2.5 Flash** | Hybrid reasoning model with excellent price-performance balance | Audio, images, video, text | Large-scale processing, low latency, high volume tasks requiring thinking |
| **Gemini 2.5 Flash-Lite** | Most cost-effective model optimized for high throughput | Audio, images, video, text | High volume, budget-conscious applications |
| **Gemini 2.0 Flash** | Balanced multimodal model built for agentic experiences | Audio, images, video, text | Production apps, agent workflows, image generation |
| **Gemini 2.0 Flash-Lite** | Entry-level model for cost efficiency | Audio, images, video, text | High-scale, cost-sensitive applications |
| **Gemini 1.5 Pro** ⚠️ | Deprecated - powerful reasoning model | Audio, images, video, text | Legacy applications (migrate to 2.5 Pro) |
| **Gemini 1.5 Flash** ⚠️ | Deprecated - versatile performance | Audio, images, video, text | Legacy applications (migrate to 2.5 Flash) |
| **Gemini 1.5 Flash-8b** ⚠️ | Deprecated - smaller, faster model | Audio, images, video, text | Legacy applications (migrate to 2.5 Flash-Lite) |

⚠️ = Deprecation planned - migrate to newer models

## Standard Pricing (Paid Tier)

### Gemini 2.5 Family (Recommended)

| Model | Input Price (≤200k tokens) | Output Price (≤200k tokens) | Audio Input |
|-------|---------------------------|----------------------------|-------------|
| **gemini-2.5-pro** | $1.25 / 1M tokens | $10.00 / 1M tokens | Same as text |
| **gemini-2.5-flash** | $0.30 / 1M tokens | $2.50 / 1M tokens | $1.00 / 1M tokens |
| **gemini-2.5-flash-lite** | $0.10 / 1M tokens | $0.40 / 1M tokens | $0.30 / 1M tokens |

**Note for 2.5 Pro:** Pricing increases for prompts >200k tokens:
- Input: $2.50 / 1M tokens
- Output: $15.00 / 1M tokens

### Gemini 2.0 Family

| Model | Input Price | Output Price | Audio Input |
|-------|-------------|-------------|-------------|
| **gemini-2.0-flash** | $0.10 / 1M tokens | $0.40 / 1M tokens | $0.70 / 1M tokens |
| **gemini-2.0-flash-lite** | $0.075 / 1M tokens | $0.30 / 1M tokens | N/A |

### Gemini 1.5 Family (Deprecated ⚠️)

| Model | Input Price | Output Price |
|-------|-------------|-------------|
| **gemini-1.5-pro** | $7.00 / 1M tokens | $21.00 / 1M tokens |
| **gemini-1.5-flash** | Varies by region | Being phased out |
| **gemini-1.5-flash-8b** | $0.35 / 1M tokens | $1.05 / 1M tokens |

## Batch API Pricing (50% Discount)

All models support batch processing with significant cost savings:

| Model | Batch Input Price | Batch Output Price |
|-------|------------------|-------------------|
| **gemini-2.5-pro** (≤200k) | $0.625 / 1M tokens | $5.00 / 1M tokens |
| **gemini-2.5-flash** | $0.15 / 1M tokens | $1.25 / 1M tokens |
| **gemini-2.5-flash-lite** | $0.05 / 1M tokens | $0.20 / 1M tokens |
| **gemini-2.0-flash** | $0.05 / 1M tokens | $0.20 / 1M tokens |
| **gemini-2.0-flash-lite** | $0.0375 / 1M tokens | $0.15 / 1M tokens |

**Batch API Benefits:**
- 50% cost reduction compared to standard pricing
- Ideal for large-scale, non-time-sensitive processing
- Available on paid tier only

## Context Caching Pricing

Context caching allows you to store frequently used context and reduce costs:

| Model | Caching Price (Text/Image/Video) | Audio Caching | Storage Price |
|-------|----------------------------------|---------------|---------------|
| **gemini-2.5-pro** (≤200k) | $0.125 / 1M tokens | N/A | $4.50 / 1M tokens/hour |
| **gemini-2.5-flash** | $0.03 / 1M tokens | $0.10 / 1M tokens | $1.00 / 1M tokens/hour |
| **gemini-2.5-flash-lite** | $0.01 / 1M tokens | $0.03 / 1M tokens | $1.00 / 1M tokens/hour |
| **gemini-2.0-flash** | $0.025 / 1M tokens | $0.175 / 1M tokens | $1.00 / 1M tokens/hour |

## Additional Features & Pricing

### Grounding with Google Search
- **Free tier:** 500-1,500 requests per day (RPD) depending on model
- **Paid tier:** $35 / 1,000 grounded prompts (after free quota)

### Grounding with Google Maps
- **Free tier:** 500-1,500 RPD depending on model
- **Paid tier:** $25 / 1,000 grounded prompts (after free quota)

### Image Generation (Gemini 2.0 Flash & 2.5 Flash Image)
- **Standard:** $0.039 per image (1024x1024px)
- **Batch:** $0.0195 per image (50% discount)

### Live API (Real-time Conversational AI)
Available for Gemini 2.5 Flash and 2.0 Flash:
- **Text input:** $0.35-$0.50 / 1M tokens
- **Audio/Image/Video input:** $2.10-$3.00 / 1M tokens
- **Text output:** $1.50-$2.00 / 1M tokens
- **Audio output:** $8.50-$12.00 / 1M tokens

## Token Information

- **1 token** ≈ 4 characters
- **100 tokens** ≈ 60-80 English words
- **1,000 tokens** ≈ 750 words or ~1 page of text
- Pricing is calculated based on both:
  - **Input tokens:** Your prompts sent to the model
  - **Output tokens:** Responses generated by the model (including "thinking tokens" for reasoning models)

## Understanding "Thinking Tokens"

Models in the 2.5 family support extended reasoning with "thinking budgets":
- The model can spend additional tokens on internal reasoning before generating output
- **You are charged for both response tokens AND thinking tokens** in the output price
- This enables more accurate and thoughtful responses for complex tasks
- Useful for: coding, mathematical reasoning, complex analysis

## Free Tier

Google AI Studio offers a generous free tier for testing and development:
- **Limited access** to most models
- **Free input & output tokens** within rate limits
- **Rate limits:** Vary by model (typically 2-15 RPM, 32k-4M TPM)
- **Usage:** Content may be used to improve Google's products
- **Best for:** Development, testing, small-scale projects

## Paid Tier Benefits

- ✅ Higher rate limits for production deployments
- ✅ Access to Context Caching
- ✅ Batch API (50% cost reduction)
- ✅ Access to Google's most advanced models
- ✅ Content NOT used to improve products
- ✅ Higher quality of service

## Model Selection Guidelines

### 1. **For budget-conscious applications**
Start with **gemini-2.5-flash-lite** or **gemini-2.0-flash-lite**
- Lowest cost options
- Good for high-volume, straightforward tasks
- Consider batch processing for additional 50% savings

### 2. **For balanced performance and cost**
Use **gemini-2.5-flash** or **gemini-2.0-flash**
- Best price-performance ratio
- Supports thinking/reasoning capabilities
- Handles multimodal inputs effectively
- Suitable for most production applications

### 3. **For complex reasoning tasks**
Choose **gemini-2.5-pro**
- Highest accuracy and reasoning capability
- Best for: complex coding, advanced analysis, challenging problems
- Supports extended context (1M tokens)
- Consider batch processing for 50% cost savings on large workloads

### 4. **For agent-based applications**
Use **gemini-2.0-flash** or **gemini-2.5-flash**
- Native tool use capabilities
- Built for agentic workflows
- Real-time features via Live API
- Native image generation (2.0 Flash)

### 5. **For production applications**
- Prefer **stable models** over experimental/preview versions
- Use **context caching** for frequently used prompts
- Implement **batch processing** for non-time-sensitive workloads
- Monitor token usage and optimize prompts

## Cost Optimization Tips

1. **Use Batch API:** Save 50% on costs for non-urgent processing
2. **Implement Context Caching:** Reuse large contexts efficiently
3. **Choose the Right Model:** Don't over-provision - use Flash/Flash-Lite for simpler tasks
4. **Optimize Prompts:** Shorter, clearer prompts reduce token usage
5. **Monitor Usage:** Track token consumption and adjust as needed
6. **Use Free Tier for Development:** Test thoroughly before moving to production

## Model Comparison Chart

| Feature | 2.5 Pro | 2.5 Flash | 2.5 Flash-Lite | 2.0 Flash |
|---------|---------|-----------|----------------|-----------|
| **Cost (Input)** | $1.25 | $0.30 | $0.10 | $0.10 |
| **Reasoning** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Speed** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Context Window** | 1M tokens | 1M tokens | 1M tokens | 1M tokens |
| **Thinking Budget** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ No |
| **Audio Input** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Image Generation** | ❌ No | ✅ Yes (via 2.5 Flash Image) | ❌ No | ✅ Yes (native) |
| **Live API** | ❌ No | ✅ Yes | ❌ No | ✅ Yes |
| **Best Use Case** | Complex tasks | Balanced workloads | High volume | Agent applications |

## Migration Guide

### From Gemini 1.5 Pro → Gemini 2.5 Pro
- Similar capabilities with improved reasoning
- Significant cost reduction: $7.00 → $1.25 per 1M input tokens
- Better performance on coding and complex reasoning

### From Gemini 1.5 Flash → Gemini 2.5 Flash
- Enhanced reasoning with thinking budgets
- Similar pricing structure
- Improved multimodal understanding

### From Gemini 1.5 Flash-8b → Gemini 2.5 Flash-Lite
- Maintained low cost profile: $0.35 → $0.10 per 1M input tokens
- Better quality outputs
- Same high throughput capabilities

## Access Tiers

### Free Tier (AI Studio)
- **Cost:** $0
- **Usage:** Testing and development
- **Limits:** Rate-limited (varies by model)
- **Data:** Used to improve products

### Paid Tier (AI Studio)
- **Cost:** Pay-as-you-go
- **Usage:** Production applications
- **Limits:** Higher rate limits
- **Data:** NOT used to improve products
- **Features:** Context caching, Batch API

### Enterprise Tier (Vertex AI)
- **Cost:** Custom pricing with volume discounts
- **Usage:** Large-scale deployments
- **Support:** Dedicated channels
- **Features:** SLAs, advanced security, provisioned throughput
- **Contact:** Google Cloud Sales

## Additional Resources

- **Official Gemini API Documentation:** [https://ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
- **Pricing Details:** [https://ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing)
- **Google AI Studio:** [https://aistudio.google.com](https://aistudio.google.com)
- **Vertex AI (Enterprise):** [https://cloud.google.com/vertex-ai](https://cloud.google.com/vertex-ai)

## Important Notes

1. **Prices are subject to change** - always verify current pricing on official documentation
2. **Regional variations** may apply for some models and features
3. **Preview/Experimental models** may have different pricing and more restrictive rate limits
4. **Vertex AI pricing** may differ from AI Studio pricing
5. **Thinking tokens** are included in output pricing for 2.5 models
6. **Audio inputs** are priced higher than text/image/video for most models

---

**Document Version:** 2.0  
**Last Updated:** November 2025  
**Compatibility:** Google AI Developer Kit (ADK)
