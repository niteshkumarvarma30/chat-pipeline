async function sendMsg() {
  const msgInput = document.getElementById('msgInput');
  const messagesDiv = document.getElementById('messages');
  const statusDiv = document.getElementById('status');
  const msg = msgInput.value.trim();
  
  if (!msg) {
    alert('Please enter a message');
    return;
  }

  const payload = { user_id: "u123", message: msg };

  try {
    // Disable input while sending
    msgInput.disabled = true;
    statusDiv.textContent = 'Sending message...';
    
    const res = await fetch('http://localhost:5000/api/chat/send', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      mode: 'cors',
      credentials: 'omit',
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      messagesDiv.innerHTML += `
        <div class="message">
          <span class="time">${new Date().toLocaleTimeString()}</span>
          <p>${data.data.message}</p>
        </div>
      `;
      msgInput.value = '';
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } else {
      throw new Error(data.error || "Failed to send message");
    }
  } catch (err) {
    console.error('Error:', err);
    alert(err.message || "Server error. Please try again.");
  } finally {
    msgInput.disabled = false;
    msgInput.focus();
  }
}
