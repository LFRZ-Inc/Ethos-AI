/**
 * Ethos AI - Client-Side Storage Example
 * Shows how to implement device memory storage in browsers/mobile apps
 */

class EthosDeviceMemory {
    constructor(deviceId, apiBaseUrl = 'http://localhost:8000') {
        this.deviceId = deviceId;
        this.apiBaseUrl = apiBaseUrl;
        this.memory = this.loadMemory();
    }

    // Load memory from device storage
    loadMemory() {
        try {
            // Browser localStorage
            if (typeof localStorage !== 'undefined') {
                const stored = localStorage.getItem(`ethos_memory_${this.deviceId}`);
                return stored ? JSON.parse(stored) : [];
            }
            
            // React Native AsyncStorage
            if (typeof AsyncStorage !== 'undefined') {
                // This would be async in React Native
                return [];
            }
            
            // Node.js file system
            if (typeof require !== 'undefined') {
                const fs = require('fs');
                const path = `./ethos_memory_${this.deviceId}.json`;
                if (fs.existsSync(path)) {
                    return JSON.parse(fs.readFileSync(path, 'utf8'));
                }
            }
            
            return [];
        } catch (error) {
            console.error('Error loading memory:', error);
            return [];
        }
    }

    // Save memory to device storage
    saveMemory(memory) {
        try {
            // Browser localStorage
            if (typeof localStorage !== 'undefined') {
                localStorage.setItem(`ethos_memory_${this.deviceId}`, JSON.stringify(memory));
                return true;
            }
            
            // React Native AsyncStorage
            if (typeof AsyncStorage !== 'undefined') {
                // AsyncStorage.setItem(`ethos_memory_${this.deviceId}`, JSON.stringify(memory));
                return true;
            }
            
            // Node.js file system
            if (typeof require !== 'undefined') {
                const fs = require('fs');
                const path = `./ethos_memory_${this.deviceId}.json`;
                fs.writeFileSync(path, JSON.stringify(memory, null, 2));
                return true;
            }
            
            return false;
        } catch (error) {
            console.error('Error saving memory:', error);
            return false;
        }
    }

    // Get memory size in KB
    getMemorySize() {
        const memoryJson = JSON.stringify(this.memory);
        return (memoryJson.length * 2) / 1024; // UTF-16 characters
    }

    // Chat with AI using device memory
    async chat(message, modelOverride = null) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/api/client/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    device_id: this.deviceId,
                    device_memory: this.memory,
                    model_override: modelOverride
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Update local memory with server response
            this.memory = data.updated_memory;
            this.saveMemory(this.memory);
            
            return {
                response: data.response,
                model: data.model,
                contextUsed: data.context_used,
                storageSize: data.storage_size_kb,
                totalConversations: this.memory.length
            };
        } catch (error) {
            console.error('Chat error:', error);
            throw error;
        }
    }

    // Get memory info
    getMemoryInfo() {
        return {
            deviceId: this.deviceId,
            totalConversations: this.memory.length,
            storageSizeKB: this.getMemorySize(),
            lastConversation: this.memory.length > 0 ? this.memory[this.memory.length - 1] : null
        };
    }

    // Clear memory
    clearMemory() {
        this.memory = [];
        this.saveMemory(this.memory);
        return true;
    }

    // Export memory
    exportMemory() {
        return {
            deviceId: this.deviceId,
            exportDate: new Date().toISOString(),
            conversations: this.memory,
            totalConversations: this.memory.length,
            storageSizeKB: this.getMemorySize()
        };
    }

    // Import memory
    importMemory(importData) {
        if (importData.deviceId === this.deviceId && importData.conversations) {
            this.memory = importData.conversations;
            this.saveMemory(this.memory);
            return true;
        }
        return false;
    }
}

// Usage Examples

// Browser Example
if (typeof window !== 'undefined') {
    // Initialize device memory
    const ethosMemory = new EthosDeviceMemory('my-phone-123');
    
    // Chat function
    async function chatWithAI(message) {
        try {
            const result = await ethosMemory.chat(message);
            console.log('AI Response:', result.response);
            console.log('Model used:', result.model);
            console.log('Context used:', result.contextUsed);
            console.log('Storage size:', result.storageSize, 'KB');
            
            // Display in UI
            document.getElementById('response').textContent = result.response;
            document.getElementById('memory-info').textContent = 
                `Memory: ${result.totalConversations} conversations, ${result.storageSize.toFixed(2)} KB`;
        } catch (error) {
            console.error('Chat failed:', error);
        }
    }
    
    // Example usage
    document.getElementById('chat-button').addEventListener('click', () => {
        const message = document.getElementById('message-input').value;
        chatWithAI(message);
    });
}

// Node.js Example
if (typeof module !== 'undefined' && module.exports) {
    const ethosMemory = new EthosDeviceMemory('my-laptop-456');
    
    async function testChat() {
        try {
            // First conversation
            const result1 = await ethosMemory.chat("Hello! I'm using my laptop.");
            console.log('First response:', result1.response);
            
            // Second conversation (should have context)
            const result2 = await ethosMemory.chat("Do you remember what I said before?");
            console.log('Second response:', result2.response);
            console.log('Context used:', result2.contextUsed);
            
            // Memory info
            const info = ethosMemory.getMemoryInfo();
            console.log('Memory info:', info);
            
        } catch (error) {
            console.error('Test failed:', error);
        }
    }
    
    // Run test
    testChat();
}

// React Native Example (pseudo-code)
/*
import AsyncStorage from '@react-native-async-storage/async-storage';

class EthosDeviceMemoryRN extends EthosDeviceMemory {
    async loadMemory() {
        try {
            const stored = await AsyncStorage.getItem(`ethos_memory_${this.deviceId}`);
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            console.error('Error loading memory:', error);
            return [];
        }
    }
    
    async saveMemory(memory) {
        try {
            await AsyncStorage.setItem(`ethos_memory_${this.deviceId}`, JSON.stringify(memory));
            return true;
        } catch (error) {
            console.error('Error saving memory:', error);
            return false;
        }
    }
}

// Usage in React Native
const ethosMemory = new EthosDeviceMemoryRN('my-phone-123');

const handleChat = async (message) => {
    try {
        const result = await ethosMemory.chat(message);
        console.log('AI Response:', result.response);
    } catch (error) {
        console.error('Chat failed:', error);
    }
};
*/

// Storage Size Calculator
function calculateStorageUsage(conversations) {
    const avgConversationSize = 2; // KB per conversation
    const totalSize = conversations * avgConversationSize;
    
    return {
        conversations: conversations,
        sizeKB: totalSize,
        sizeMB: totalSize / 1024,
        storageType: {
            '50 conversations': '100 KB',
            '100 conversations': '200 KB', 
            '500 conversations': '1 MB',
            '1000 conversations': '2 MB'
        }
    };
}

// Example storage calculations
console.log('Storage Usage Examples:');
console.log(calculateStorageUsage(50));   // 100 KB
console.log(calculateStorageUsage(100));  // 200 KB
console.log(calculateStorageUsage(500));  // 1 MB
console.log(calculateStorageUsage(1000)); // 2 MB

module.exports = { EthosDeviceMemory, calculateStorageUsage };
