document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded - script starting');
    
    // Check if elements exist
    const roomId = document.getElementById('room-id');
    console.log('Room ID element exists:', !!roomId);
    
    const toggleAudioButton = document.getElementById('toggle-audio');
    console.log('Toggle audio button exists:', !!toggleAudioButton);
    
    const toggleVideoButton = document.getElementById('toggle-video');
    console.log('Toggle video button exists:', !!toggleVideoButton);
    
    const screenContainer = document.querySelector('.screen-container');
    console.log('Screen container exists:', !!screenContainer);
    
    const chatInput = document.getElementById('chat-input');
    const chatForm = document.getElementById('chat-form');
    const chatMessages = document.getElementById('chat-messages');

    const wsUrl = `wss://${window.location.host}/ws/room/${roomId.getAttribute('data-room-id')}/`;
    const chatSocket = new WebSocket(wsUrl);

    chatSocket.onopen = () => {
        console.log('WebSocket connection established.');
    };

    chatSocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
            const messageElement = document.createElement('div');
            messageElement.classList.add('message', data.username === 'You' ? 'own' : 'other');
            messageElement.textContent = `${data.username}: ${data.message}`;
            chatMessages.appendChild(messageElement);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    };

    chatSocket.onclose = (event) => {
        console.error('WebSocket connection closed:', event);
    };

    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const message = chatInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                type: 'message',
                message: message,
            }));
            chatInput.value = '';
        }
    });

    const screenButton = document.getElementById('screen-button');
    const videoElement = document.getElementById('remote-screen-display');
    let screenStream = null;

    screenButton.addEventListener('click', async () => {
        try {
            // Check if screen sharing is already active
            if (screenStream) {
                stopScreenSharing();
                return;
            }

            // Request screen sharing
            screenStream = await navigator.mediaDevices.getDisplayMedia({
                video: true,
                audio: false, // Set to true if you want to share audio
            });

            // Display the shared screen in the video element
            videoElement.srcObject = screenStream;

            // Handle when the user stops sharing
            screenStream.getVideoTracks()[0].addEventListener('ended', () => {
                stopScreenSharing();
            });

            console.log('Screen sharing started.');
        } catch (error) {
            console.error('Error starting screen sharing:', error);
        }
    });

    function stopScreenSharing() {
        if (screenStream) {
            screenStream.getTracks().forEach((track) => track.stop());
            screenStream = null;
            videoElement.srcObject = null;
            console.log('Screen sharing stopped.');
        }
    }

    const leaveRoomButton = document.getElementById('leave-room');

    leaveRoomButton.addEventListener('click', () => {
        const confirmLeave = confirm('Are you sure you want to leave the room?');
        if (confirmLeave){
            window.location.href = '/join-room/';
        }
    });

    // Initialize media with error handling
    initializeMediaWithFallback();
    
    async function initializeMediaWithFallback() {
        console.log('Attempting to initialize media...');
        try {
            // Check if getUserMedia is supported
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('getUserMedia is not supported in this browser');
            }
            
            // Create video element first
            localVideoElement = document.createElement('video');
            localVideoElement.autoplay = true;
            localVideoElement.muted = true;
            localVideoElement.playsinline = true;
            localVideoElement.controls = true;
            localVideoElement.classList.add('local-video');
            localVideoElement.style.width = '150px';
            localVideoElement.style.position = 'absolute';
            localVideoElement.style.bottom = '10px';
            localVideoElement.style.right = '10px';
            localVideoElement.style.borderRadius = '8px';
            localVideoElement.style.border = '2px solid #9c5bff';
            localVideoElement.style.zIndex = '10';
            
            console.log('Local video element created');
            
            // Add to DOM
            if (screenContainer) {
                screenContainer.appendChild(localVideoElement);
                console.log('Local video element added to DOM');
            } else {
                document.body.appendChild(localVideoElement);
                console.log('Added to body as fallback');
            }
            
            // Get user media with constraints
            try {
                localStream = await navigator.mediaDevices.getUserMedia({
                    video: true,
                    audio: true
                });
                console.log('Media stream obtained successfully');
                
                // Attach stream to video element
                localVideoElement.srcObject = localStream;
                console.log('Stream attached to video element');
                const videoTrack = localStream.getVideoTracks()[0];
                if (videoTrack) {
                    videoTrack.enabled = false;
                    console.log('Video track disabled by default');
                    
                    // Update toggle button to show disabled state
                    if (toggleVideoButton) {
                        toggleVideoButton.classList.add('bg-red-600');
                    }
                }
            } catch (mediaError) {
                console.error('Media error:', mediaError);
                // Try with just video as fallback
                try {
                    localStream = await navigator.mediaDevices.getUserMedia({
                        video: true,
                        audio: false
                    });
                    console.log('Video-only stream obtained as fallback');
                    localVideoElement.srcObject = localStream;
                } catch (videoOnlyError) {
                    console.error('Even video-only failed:', videoOnlyError);
                }
            }
        } catch (error) {
            console.error('Media initialization failed:', error);
        }
    }

    // Toggle audio functionality
    if (toggleAudioButton) {
        toggleAudioButton.addEventListener('click', () => {
            console.log('Toggle audio button clicked');
            if (localStream) {
                const audioTrack = localStream.getAudioTracks()[0];
                if (audioTrack) {
                    audioTrack.enabled = !audioTrack.enabled;
                    toggleAudioButton.classList.toggle('bg-red-600', !audioTrack.enabled);
                    console.log(`Audio ${audioTrack.enabled ? 'enabled' : 'disabled'}`);
                }
            }
        });
    } else {
        console.error('Toggle audio button not found');
    }

    // Toggle video functionality
    if (toggleVideoButton) {
        toggleVideoButton.addEventListener('click', () => {
            console.log('Toggle video button clicked');
            if (localStream) {
                const videoTrack = localStream.getVideoTracks()[0];
                if (videoTrack) {
                    videoTrack.enabled = !videoTrack.enabled;
                    toggleVideoButton.classList.toggle('bg-red-600', !videoTrack.enabled);
                    console.log(`Video ${videoTrack.enabled ? 'enabled' : 'disabled'}`);
                }
            }
        });
    } else {
        console.error('Toggle video button not found');
    }
});
