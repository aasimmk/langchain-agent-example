<template>
  <div class="chat-container">
    <h1>Langchain Text2SQL</h1>
    <div class="messages" ref="messagesContainer">
      <div
        v-for="(message, index) in messages"
        :key="index"
        :class="['message', message.sender === 'You' ? 'sent' : 'received']"
      >
        <strong>{{ message.sender }}:</strong> <span v-html="message.text"></span>
      </div>
      <div v-if="isLoading" class="message received">
        <strong>Server:</strong> <span class="loading">Thinking...</span>
      </div>
    </div>
    <form @submit.prevent="sendMessage" class="message-form">
      <input
        v-model="newMessage"
        type="text"
        placeholder="Type your message..."
        required
        @keydown.enter.prevent="sendMessage"
      />
      <button type="submit" :disabled="isLoading">Send</button>
    </form>
  </div>
</template>

<script>
import apiService from '@/services/apiService';
import { ref, onBeforeUnmount, watch, nextTick} from 'vue';

export default {
  name: 'ChatView',
  setup() {
    const messages = ref([]);
    const newMessage = ref('');
    const isLoading = ref(false);
    const messagesContainer = ref(null);
    // let conversationStream = null; // To hold the streaming process

    /**
     * Sends a message and handles the streaming response.
     */
    const sendMessage = async () => {
      if (newMessage.value.trim() === '') return;

      const question = newMessage.value.trim();

      // Push user's message to the chat
      messages.value.push({
        sender: 'You',
        text: question,
      });

      // Clear the input field
      newMessage.value = '';
      isLoading.value = true;

      try {
        // Start the conversation stream
        await apiService.startConversation(
          question,
          handleIncomingMessage,
          handleError,
          handleEnd
        );
      } catch (error) {
        console.error('Error initiating conversation:', error.message);
        messages.value.push({
          sender: 'Error',
          text: 'Failed to initiate conversation.',
        });
        isLoading.value = false;
      }
    };

    /**
     * Handles incoming messages from the stream.
     * @param {string} data - The incoming data chunk.
     */
    const handleIncomingMessage = (data) => {
      if (data) {
        // Update the last server message or create a new one
        if (
          messages.value.length > 0 &&
          messages.value[messages.value.length - 1].sender === 'Server'
        ) {
          messages.value[messages.value.length - 1].text += data;
        } else {
          messages.value.push({
            sender: 'Server',
            text: data,
          });
        }
      }
    };

    /**
     * Handles errors from the stream.
     * @param {Error} error - The error object.
     */
    const handleError = (error) => {
      console.error('Stream Error:', error.message);
      messages.value.push({
        sender: 'Error',
        text: 'An error occurred while receiving the response.',
      });
      isLoading.value = false;
    };

    /**
     * Handles the end of the stream.
     */
    const handleEnd = () => {
      isLoading.value = false;
      console.log('Conversation stream ended.');
    };

    /**
     * Automatically scrolls the messages container to the bottom when new messages arrive.
     */
    const scrollToBottom = () => {
      nextTick(() => {
        if (messagesContainer.value) {
          messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
      });
    };

    // Watch for changes in messages to auto-scroll
    watch(messages, () => {
      scrollToBottom();
    });

    /**
     * Cleanup: Close the conversation stream when the component is unmounted
     */
    onBeforeUnmount(() => {
      // If your streamService provided a way to disconnect, invoke it here.
      // Currently, fetchStream does not maintain a connection to close.
      // If you need to abort the fetch, consider using an AbortController.
      // This example assumes the stream ends naturally.
    });

    return {
      messages,
      newMessage,
      sendMessage,
      isLoading,
      messagesContainer,
    };
  },
};
</script>

<style scoped>
.chat-container {
  max-width: 1000px;
  margin: 50px auto;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.messages {
  border: 1px solid #ccc;
  height: 600px;
  overflow-y: auto;
  padding: 10px;
  margin-bottom: 10px;
  background-color: #f9f9f9;
}

.message {
  margin-bottom: 10px;
  padding: 8px 12px;
  border-radius: 4px;
  max-width: 80%;
  word-wrap: break-word;
}

.sent {
  background-color: #dcf8c6;
  align-self: flex-end;
  margin-left: auto;
}

.received {
  background-color: #ffffff;
  align-self: flex-start;
  margin-right: auto;
}

.loading {
  font-style: italic;
  color: #888;
}

.message-form {
  display: flex;
}

.message-form input {
  flex: 1;
  padding: 10px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.message-form button {
  padding: 10px 20px;
  margin-left: 10px;
  font-size: 16px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.message-form button:disabled {
  background-color: #a5d6a7;
  cursor: not-allowed;
}
</style>
