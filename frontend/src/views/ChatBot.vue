<template>
  <div class="chat-container">
    <h2>Chat Room</h2>
    <div class="messages">
      <div v-for="(message, index) in messages" :key="index" class="message">
        <strong>{{ message.sender }}:</strong> {{ message.text }}
      </div>
    </div>
    <form @submit.prevent="sendMessage" class="chat-form">
      <input
        v-model="userMessage"
        type="text"
        placeholder="Type your message..."
        class="chat-input"
        required
      />
      <button type="submit" class="send-button" :disabled="isStreaming">Send</button>
    </form>
  </div>
</template>

<script>
import api from '@/services/api';
export default {
  data() {
    return {
      userMessage: '', // Message typed by the user
      messages: [], // Array of chat messages
      isStreaming: false, // Controls if we're streaming a response
    };
  },
  methods: {
    async sendMessage() {
      // Add the user's message to the chat
      this.messages.push({sender: 'You', text: this.userMessage});

      // Save userMessage locally and clear the input field
      // const userMessage = this.userMessage;
      this.userMessage = '';

      // Simulate starting streaming response from the bot
      this.isStreaming = true;

      // Add a new bot message placeholder for streaming text
      const botMessage = {sender: 'Bot', text: ''};
      this.messages.push(botMessage);

      try {
        // Call a function that simulates streaming data (replace with real API)
        await this.streamBotResponse(botMessage);
      } catch (error) {
        botMessage.text = 'Oops! Something went wrong during streaming.';
      } finally {
        this.isStreaming = false;
      }
    },
    // Function that simulates an API call with streaming response
    async streamBotResponse(botMessage) {
      // Replace this URL with your streaming API endpoint
      const response = await api.get(`http://localhost:8000/conversation/?question=${this.userMessage}`);

      // Create a readable stream to handle the chunks of data
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let done = false;

      // Continuously read from the stream until it's done
      while (!done) {
        const {value, done: streamDone} = await reader.read();
        done = streamDone;

        // Decode and append the chunk to the bot message
        botMessage.text += decoder.decode(value, {stream: !done});

        // We want to trigger the reactivity system in Vue, so we use $set
        this.$forceUpdate();
      }
    }
  }
};
</script>

<style scoped>
.chat-container {
  max-width: 500px;
  margin: 0 auto;
  border: 1px solid #ccc;
  padding: 1rem;
  border-radius: 5px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.messages {
  flex-grow: 1;
  overflow-y: auto;
  max-height: 300px;
  margin-bottom: 1rem;
}

.message {
  margin: 0.5rem 0;
}

.chat-form {
  display: flex;
  justify-content: space-between;
}

.chat-input {
  flex-grow: 1;
  padding: 0.5rem;
  border-radius: 5px;
  border: 1px solid #ccc;
  margin-right: 0.5rem;
}

.send-button {
  padding: 0.5rem 1rem;
  border: none;
  background-color: #007bff;
  color: white;
  border-radius: 5px;
  cursor: pointer;
}

.send-button:hover {
  background-color: #0056b3;
}

.send-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
</style>
