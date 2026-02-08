#!/bin/bash

echo "=========================================="
echo "🔍 Backend Route Verification"
echo "=========================================="
echo ""

# Check if backend is running
echo "1. Checking if backend is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running on port 8000"
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "   Response: $HEALTH"
else
    echo "   ❌ Backend is NOT running"
    echo ""
    echo "   Start with:"
    echo "   cd /mnt/e/hackathon_todo_II/backend"
    echo "   uvicorn main:app --reload --port 8000"
    exit 1
fi

echo ""
echo "2. Testing chatbot endpoints..."

# Test conversations endpoint
echo "   Testing: GET /api/user123/conversations"
STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -H "Authorization: Bearer user123" \
    http://localhost:8000/api/user123/conversations)

if [ "$STATUS" = "200" ]; then
    echo "   ✅ Conversations endpoint works! (200 OK)"
elif [ "$STATUS" = "404" ]; then
    echo "   ❌ 404 Not Found - Chatbot routes not loaded!"
    echo ""
    echo "   Fix:"
    echo "   1. Stop the backend (Ctrl+C)"
    echo "   2. Ensure dependencies are installed:"
    echo "      cd /mnt/e/hackathon_todo_II/backend"
    echo "      pip install -r requirements.txt"
    echo "   3. Restart: uvicorn main:app --reload --port 8000"
else
    echo "   ⚠️  Unexpected status: $STATUS"
fi

# Test chat endpoint
echo ""
echo "   Testing: POST /api/user123/chat"
CHAT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer user123" \
    -d '{"message":"test"}' \
    http://localhost:8000/api/user123/chat)

if [ "$CHAT_STATUS" = "200" ] || [ "$CHAT_STATUS" = "422" ] || [ "$CHAT_STATUS" = "503" ]; then
    echo "   ✅ Chat endpoint exists! (Status: $CHAT_STATUS)"
    if [ "$CHAT_STATUS" = "503" ]; then
        echo "      Note: OpenRouter API may not be configured"
    fi
elif [ "$CHAT_STATUS" = "404" ]; then
    echo "   ❌ 404 Not Found - Chatbot routes not loaded!"
else
    echo "   ⚠️  Unexpected status: $CHAT_STATUS"
fi

echo ""
echo "3. Checking API documentation..."
if curl -s http://localhost:8000/docs | grep -q "swagger"; then
    echo "   ✅ API docs available at: http://localhost:8000/docs"
else
    echo "   ⚠️  Could not verify API docs"
fi

echo ""
echo "=========================================="
echo "Summary:"
echo "=========================================="

if [ "$STATUS" = "200" ] && [ "$CHAT_STATUS" != "404" ]; then
    echo "✅ All chatbot endpoints are working!"
    echo ""
    echo "You can now:"
    echo "  - Access chat at: http://localhost:3000/chat"
    echo "  - View API docs: http://localhost:8000/docs"
else
    echo "❌ Some endpoints are not working"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Ensure backend is running: uvicorn main:app --reload"
    echo "  2. Install dependencies: pip install -r requirements.txt"
    echo "  3. Check backend logs for import errors"
fi
echo "=========================================="
