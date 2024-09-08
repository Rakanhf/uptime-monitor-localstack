// Include Day.js CDN for the JavaScript file
const dayjsScript = document.createElement('script');
dayjsScript.src = "https://cdn.jsdelivr.net/npm/dayjs@1/dayjs.min.js";
document.head.appendChild(dayjsScript);

// Include UTC plugin for Day.js
const utcPlugin = document.createElement('script');
utcPlugin.src = "https://cdn.jsdelivr.net/npm/dayjs@1/plugin/utc.js";
document.head.appendChild(utcPlugin);

// Wait for the script to load and extend Day.js with UTC support
utcPlugin.onload = () => {
    dayjs.extend(dayjs_plugin_utc);

    // Fetch websites when the page loads
    window.onload = fetchWebsites;
};

let urlToDelete = '';

// Function to fetch and render website data from the API
async function fetchWebsites() {
    try {
        const response = await fetch('https://uptime.execute-api.localhost.localstack.cloud:4566/dev/website');
        const data = await response.json();
        const websites = data.websites;

        const tableBody = document.getElementById('website-table-body');
        tableBody.innerHTML = ''; // Clear previous content

        websites.forEach(website => {
            const statusColor = getStatusColor(website.Status);
            const timeAgo = formatTimeAgo(website.LastChecked);
            const row = `
                <tr class="border-b last:border-none">
                    <td class="py-3 px-4">
                        <div class="flex items-center justify-between">
                            <div>
                                <div class="flex items-center">
                                    <span class="text-lg font-medium">${website.Url}</span>
                                    <span class="ml-4 ${statusColor} px-1.5 py-0.5 text-xs rounded">${website.Status}</span>
                                </div>
                                <span class="block text-gray-500 text-sm">Last checked ${timeAgo}</span>
                            </div>
                            <a href="#" class="text-blue-600 hover:underline" onclick="confirmDelete('${website.Url}')">Delete</a>
                        </div>
                    </td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    } catch (error) {
        console.error('Error fetching websites:', error);
    }
}

// Function to format the time difference using Day.js
function formatTimeAgo(lastChecked) {
    const checkedTime = dayjs.utc(lastChecked); // Parse the datetime in UTC
    const now = dayjs.utc(); // Get current time in UTC
    const diffInMinutes = now.diff(checkedTime, 'minute'); // Get difference in minutes
    if (lastChecked === "NEVER"){
        return "N/A";
    }

    if (diffInMinutes < 1) {
        return "just now";
    } else if (diffInMinutes === 1) {
        return "1 minute ago";
    } else if (diffInMinutes < 60) {
        return `${diffInMinutes} minutes ago`;
    } else {
        const diffInHours = now.diff(checkedTime, 'hour');
        if (diffInHours === 1) {
            return "1 hour ago";
        } else if (diffInHours < 24) {
            return `${diffInHours} hours ago`;
        } else {
            const diffInDays = now.diff(checkedTime, 'day');
            if (diffInDays === 1) {
                return "1 day ago";
            } else {
                return `${diffInDays} days ago`;
            }
        }
    }
}

// Function to return the appropriate color class based on the status
function getStatusColor(status) {
    switch (status) {
        case 'UP':
            return 'text-green-800 bg-green-100';
        case 'DOWN':
            return 'text-red-800 bg-red-100';
        default:
            return 'text-gray-800 bg-gray-100'; // For UNKNOWN or other statuses
    }
}

// Function to handle the response and display the error inside the modal
function handleResponse(event) {
    const response = JSON.parse(event.detail.xhr.response);
    
    const errorMessageContainer = document.getElementById('modal-error-message');
    errorMessageContainer.innerHTML = ''; // Clear previous messages

    if (response.error) {
        // Display error message in the modal
        errorMessageContainer.innerHTML = `<div class="p-2 text-sm text-red-800 bg-red-50 rounded-lg">${response.error}</div>`;
    } else {
        // Close modal and refresh the websites list
        document.getElementById('urlInput').value = ''; // Clear the input
        toggleModal('add'); // Close modal after successful addition
        fetchWebsites(); // Refresh the table after addition
    }
}

// Function to toggle modals (for add and delete)
function toggleModal(modalType) {
    const modal = modalType === 'add' ? document.getElementById('modal') : document.getElementById('deleteModal');
    modal.classList.toggle('hidden');
    const errorMessageContainer = document.getElementById('modal-error-message');
    if (errorMessageContainer) errorMessageContainer.innerHTML = ''; // Clear error messages if modal is for adding
}

// Function to confirm deletion
function confirmDelete(url) {
    urlToDelete = url;
    document.getElementById('delete-confirmation-text').textContent = `Are you sure you want to delete ${url}?`;
    toggleModal('delete');
}

// Function to delete a website
async function deleteWebsite() {
    try {
        const response = await fetch(`https://uptime.execute-api.localhost.localstack.cloud:4566/dev/website?url=${encodeURIComponent(urlToDelete)}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            toggleModal('delete'); // Close the delete modal
            fetchWebsites(); // Refresh the table
        } else {
            console.error('Failed to delete website');
        }
    } catch (error) {
        console.error('Error deleting website:', error);
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Attach delete button logic to the confirmation modal
    document.getElementById('confirm-delete').addEventListener('click', deleteWebsite);
});
