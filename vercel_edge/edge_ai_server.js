// Vercel Edge Function for AI Processing
// This runs on Vercel's edge network worldwide

export default async function handler(req, res) {
  // Enable CORS for edge function
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    const { method, url } = req;

    // Route handling
    if (method === 'GET' && url === '/api/health') {
      return res.json({
        status: 'healthy',
        platform: 'vercel-edge',
        location: req.headers['x-vercel-ip-country'] || 'unknown',
        timestamp: new Date().toISOString()
      });
    }

    if (method === 'POST' && url === '/api/chat') {
      const { message, model = 'phi:1b' } = req.body;

      // Edge AI processing
      const response = await processAIRequest(message, model);
      
      return res.json({
        response: response,
        model: model,
        platform: 'vercel-edge',
        processing_time: Date.now() - req.startTime
      });
    }

    if (method === 'GET' && url === '/api/models') {
      return res.json({
        models: [
          {
            name: 'phi:1b',
            size: '1.6GB',
            type: 'text_generation',
            available: true
          },
          {
            name: 'llama2:1b',
            size: '1.1GB', 
            type: 'text_generation',
            available: true
          }
        ],
        platform: 'vercel-edge'
      });
    }

    // Default response
    return res.json({
      message: 'Ethos AI Edge Server',
      version: '1.0.0',
      platform: 'vercel-edge',
      endpoints: [
        '/api/health',
        '/api/chat',
        '/api/models'
      ]
    });

  } catch (error) {
    console.error('Edge function error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: error.message
    });
  }
}

async function processAIRequest(message, model) {
  // Edge AI processing logic
  // This would integrate with lightweight AI models
  
  // For now, return a mock response
  // In production, this would call actual AI models
  
  const responses = {
    'phi:1b': `[Phi 1B Edge Response] ${message}`,
    'llama2:1b': `[Llama2 1B Edge Response] ${message}`
  };

  return responses[model] || responses['phi:1b'];
}

// Edge function configuration
export const config = {
  runtime: 'edge',
  regions: ['iad1', 'sfo1', 'hnd1', 'fra1'], // Global edge locations
  maxDuration: 30, // 30 seconds max
};
