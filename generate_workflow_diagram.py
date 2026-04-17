"""
Generate Workflow Diagram for EveryLingua AI Project
Creates a PNG image showing the system architecture and workflow
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, ConnectionPatch
import numpy as np

def create_workflow_diagram():
    """Create the main workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(24, 18), facecolor='white')
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 18)
    ax.axis('off')
    
    # Title
    ax.text(12, 17.5, 'EveryLingua AI - System Architecture & Workflow', 
            fontsize=24, fontweight='bold', ha='center', va='center',
            color='#1a1a2e')
    ax.text(12, 17, 'Multilingual Motorcycle Dealership Voice Assistant', 
            fontsize=14, ha='center', va='center', color='#4a4a6a', style='italic')
    
    # Color scheme
    colors = {
        'client': '#e8f4f8',
        'client_border': '#3498db',
        'api': '#fff3e6',
        'api_border': '#e67e22',
        'service': '#e8f8e8',
        'service_border': '#27ae60',
        'external': '#f8e8f8',
        'external_border': '#9b59b6',
        'data': '#f8f8e8',
        'data_border': '#f39c12',
        'arrow': '#2c3e50',
        'text': '#1a1a2e'
    }
    
    # ==================== CLIENT LAYER ====================
    # Layer background
    client_bg = FancyBboxPatch((0.5, 14), 23, 2.5, boxstyle="round,pad=0.1",
                                facecolor=colors['client'], edgecolor=colors['client_border'],
                                linewidth=2, alpha=0.7)
    ax.add_patch(client_bg)
    ax.text(1, 16.2, 'CLIENT LAYER', fontsize=12, fontweight='bold', color=colors['client_border'])
    
    # Client boxes
    client_boxes = [
        (2, 14.5, 'index.html\n(Main App)'),
        (6.5, 14.5, 'register.html\n(Registration)'),
        (11, 14.5, 'dealer_dashboard\n.html'),
        (15.5, 14.5, 'dealer_locator\n.html'),
        (20, 14.5, 'Browser\nSpeech API')
    ]
    
    for x, y, text in client_boxes:
        box = FancyBboxPatch((x, y), 3, 1.3, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor=colors['client_border'],
                             linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.5, y+0.65, text, fontsize=9, ha='center', va='center', 
                fontweight='bold', color=colors['text'])
    
    # ==================== API LAYER ====================
    api_bg = FancyBboxPatch((0.5, 10.5), 23, 3, boxstyle="round,pad=0.1",
                            facecolor=colors['api'], edgecolor=colors['api_border'],
                            linewidth=2, alpha=0.7)
    ax.add_patch(api_bg)
    ax.text(1, 13.2, 'API LAYER (Flask - app.py)', fontsize=12, fontweight='bold', 
            color=colors['api_border'])
    
    # API box
    api_box = FancyBboxPatch((2, 10.8), 20, 2, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor=colors['api_border'],
                             linewidth=1.5)
    ax.add_patch(api_box)
    
    # API endpoints text
    endpoints_text = [
        '/api/chat • /api/voice-command • /api/ivr/respond',
        '/api/tts/generate • /api/tts/chat • /api/tts/audio',
        '/api/auth/* • /api/register/* • /api/bikes • /api/services',
        '/api/test-ride-booking • /api/service-booking • /api/human-agent/*'
    ]
    for i, text in enumerate(endpoints_text):
        ax.text(12, 12.4 - i*0.4, text, fontsize=8, ha='center', va='center', 
                color=colors['text'], family='monospace')
    
    # ==================== SERVICE LAYER ====================
    service_bg = FancyBboxPatch((0.5, 5), 23, 5, boxstyle="round,pad=0.1",
                                facecolor=colors['service'], edgecolor=colors['service_border'],
                                linewidth=2, alpha=0.7)
    ax.add_patch(service_bg)
    ax.text(1, 9.7, 'SERVICE LAYER (Python Modules)', fontsize=12, fontweight='bold', 
            color=colors['service_border'])
    
    # Service boxes - Row 1
    service_boxes_r1 = [
        (1.5, 7.5, 'openai_client.py\n\nGemini AI\nChat & TTS'),
        (6, 7.5, 'dealership_logic.py\n\nBike Inventory\nEMI Calculator'),
        (10.5, 7.5, 'voice_assistant.py\n\nSpeech Recog\nWake Word'),
        (15, 7.5, 'tts_service.py\n\ngTTS Audio\nMultilingual'),
        (19.5, 7.5, 'crm_integration.py\n\nCRM System\nBookings')
    ]
    
    for x, y, text in service_boxes_r1:
        box = FancyBboxPatch((x, y), 3.5, 1.8, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor=colors['service_border'],
                             linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.75, y+0.9, text, fontsize=7, ha='center', va='center', 
                fontweight='bold', color=colors['text'])
    
    # Service boxes - Row 2
    service_boxes_r2 = [
        (3, 5.3, 'human_agent_\nfallback.py\n\nEscalation'),
        (8, 5.3, 'otp_service.py\n\nEmail/SMS\nVerification'),
        (13, 5.3, 'user_db.py\n\nUser Auth\nSessions'),
        (18, 5.3, 'location_service.py\n\nNearest Dealer')
    ]
    
    for x, y, text in service_boxes_r2:
        box = FancyBboxPatch((x, y), 3.5, 1.8, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor=colors['service_border'],
                             linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.75, y+0.9, text, fontsize=7, ha='center', va='center', 
                fontweight='bold', color=colors['text'])
    
    # ==================== EXTERNAL SERVICES ====================
    ext_bg = FancyBboxPatch((0.5, 2.5), 11, 2, boxstyle="round,pad=0.1",
                            facecolor=colors['external'], edgecolor=colors['external_border'],
                            linewidth=2, alpha=0.7)
    ax.add_patch(ext_bg)
    ax.text(1, 4.2, 'EXTERNAL SERVICES', fontsize=11, fontweight='bold', 
            color=colors['external_border'])
    
    ext_boxes = [
        (1, 2.7, 'Google\nGemini API'),
        (4, 2.7, 'Google\nCloud TTS'),
        (7, 2.7, 'SMTP\n(Gmail)'),
        (10, 2.7, 'SMS\nGateway')
    ]
    
    for x, y, text in ext_boxes:
        box = FancyBboxPatch((x, y), 2.5, 1.2, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor=colors['external_border'],
                             linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.25, y+0.6, text, fontsize=8, ha='center', va='center', 
                fontweight='bold', color=colors['text'])
    
    # ==================== DATA LAYER ====================
    data_bg = FancyBboxPatch((12, 2.5), 11.5, 2, boxstyle="round,pad=0.1",
                             facecolor=colors['data'], edgecolor=colors['data_border'],
                             linewidth=2, alpha=0.7)
    ax.add_patch(data_bg)
    ax.text(12.5, 4.2, 'DATA LAYER (SQLite)', fontsize=11, fontweight='bold', 
            color=colors['data_border'])
    
    data_boxes = [
        (12.5, 2.7, 'users.db\n(Users, Sessions)'),
        (16.5, 2.7, 'dealership_crm.db\n(Customers, Bookings)'),
        (20.5, 2.7, 'tts_output/\n(Audio Files)')
    ]
    
    for x, y, text in data_boxes:
        box = FancyBboxPatch((x, y), 3.5, 1.2, boxstyle="round,pad=0.05",
                             facecolor='white', edgecolor=colors['data_border'],
                             linewidth=1.5)
        ax.add_patch(box)
        ax.text(x+1.75, y+0.6, text, fontsize=8, ha='center', va='center', 
                fontweight='bold', color=colors['text'])
    
    # ==================== ARROWS ====================
    arrow_style = dict(arrowstyle='->', color=colors['arrow'], lw=2, 
                       connectionstyle='arc3,rad=0')
    
    # Client to API
    ax.annotate('', xy=(12, 13.5), xytext=(12, 14.5),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    ax.text(13, 14, 'HTTP/REST', fontsize=8, color=colors['arrow'])
    
    # API to Service
    ax.annotate('', xy=(12, 9.5), xytext=(12, 10.8),
                arrowprops=dict(arrowstyle='->', color=colors['arrow'], lw=2))
    
    # Service to External
    ax.annotate('', xy=(6, 4.5), xytext=(6, 5.3),
                arrowprops=dict(arrowstyle='<->', color=colors['external_border'], lw=1.5))
    
    # Service to Data
    ax.annotate('', xy=(18, 4.5), xytext=(18, 5.3),
                arrowprops=dict(arrowstyle='<->', color=colors['data_border'], lw=1.5))
    
    # ==================== SUPPORTED LANGUAGES BOX ====================
    lang_box = FancyBboxPatch((0.5, 0.3), 10, 1.8, boxstyle="round,pad=0.1",
                              facecolor='#e8e8ff', edgecolor='#5555aa',
                              linewidth=2, alpha=0.9)
    ax.add_patch(lang_box)
    ax.text(5.5, 1.8, '[LANGUAGES] Supported Languages', fontsize=10, fontweight='bold', 
            ha='center', color='#333366')
    ax.text(5.5, 1.2, 'English • Hindi • Tamil • Telugu • Kannada', fontsize=8, 
            ha='center', color='#333366')
    ax.text(5.5, 0.7, 'Marathi • Gujarati • Bengali • Malayalam', fontsize=8, 
            ha='center', color='#333366')
    
    # ==================== KEY FEATURES BOX ====================
    feat_box = FancyBboxPatch((11, 0.3), 12.5, 1.8, boxstyle="round,pad=0.1",
                              facecolor='#fff8e8', edgecolor='#aa8855',
                              linewidth=2, alpha=0.9)
    ax.add_patch(feat_box)
    ax.text(17.25, 1.8, '[FEATURES] Key Features', fontsize=10, fontweight='bold', 
            ha='center', color='#664422')
    ax.text(17.25, 1.2, 'AI Chat • Voice Recognition • Text-to-Speech • EMI Calculator', 
            fontsize=8, ha='center', color='#664422')
    ax.text(17.25, 0.7, 'Test Ride Booking • Service Booking • Human Agent Fallback', 
            fontsize=8, ha='center', color='#664422')
    
    plt.tight_layout()
    return fig

def create_chat_workflow_diagram():
    """Create the chat workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12), facecolor='white')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(8, 11.5, 'Chat/Voice Workflow', fontsize=20, fontweight='bold', 
            ha='center', va='center', color='#1a1a2e')
    
    # Workflow steps
    steps = [
        (2, 10, 'User Input\n(Text/Voice)', '#3498db'),
        (6, 10, 'API Endpoint\n/api/chat', '#e67e22'),
        (10, 10, 'Language\nDetection', '#9b59b6'),
        (14, 10, 'Context\nBuilding', '#27ae60'),
        (2, 7, 'Bike Data\nInventory', '#16a085'),
        (6, 7, 'Service\nPackages', '#16a085'),
        (10, 7, 'Dealer\nInfo', '#16a085'),
        (14, 7, 'Gemini AI\nProcessing', '#e74c3c'),
        (8, 4, 'Response\nGeneration', '#2980b9'),
        (8, 1.5, 'TTS Audio\n(if voice)', '#8e44ad'),
    ]
    
    for x, y, text, color in steps:
        box = FancyBboxPatch((x-1.2, y-0.6), 2.4, 1.2, boxstyle="round,pad=0.1",
                             facecolor='white', edgecolor=color, linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=9, ha='center', va='center', 
                fontweight='bold', color='#1a1a2e')
    
    # Arrows
    arrows = [
        ((3.2, 10), (4.8, 10)),
        ((7.2, 10), (8.8, 10)),
        ((11.2, 10), (12.8, 10)),
        ((14, 9.4), (14, 7.6)),
        ((12.8, 7), (11.2, 7)),
        ((8.8, 7), (7.2, 7)),
        ((4.8, 7), (3.2, 7)),
        ((2, 7.6), (2, 9.4)),
        ((6, 7.6), (6, 9.4)),
        ((10, 7.6), (10, 9.4)),
        ((14, 6.4), (9.2, 4)),
        ((8, 3.4), (8, 2.1)),
    ]
    
    for start, end in arrows:
        ax.annotate('', xy=end, xytext=start,
                    arrowprops=dict(arrowstyle='->', color='#34495e', lw=1.5))
    
    plt.tight_layout()
    return fig

def create_user_journey_diagram():
    """Create user journey workflow diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(18, 10), facecolor='white')
    ax.set_xlim(0, 18)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(9, 9.5, 'User Journey - Complete Flow', fontsize=20, fontweight='bold', 
            ha='center', va='center', color='#1a1a2e')
    
    # Row 1 - Registration
    ax.text(1, 8, 'Registration Flow', fontsize=12, fontweight='bold', color='#3498db')
    reg_steps = [
        (1, 7, 'Visit\nSite'),
        (4, 7, 'Register\nPage'),
        (7, 7, 'Enter\nDetails'),
        (10, 7, 'OTP\nVerification'),
        (13, 7, 'Account\nCreated'),
        (16, 7, 'Login\n✓')
    ]
    for x, y, text in reg_steps:
        box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, boxstyle="round,pad=0.05",
                             facecolor='#e8f4fc', edgecolor='#3498db', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8, ha='center', va='center', fontweight='bold')
    for i in range(5):
        ax.annotate('', xy=(reg_steps[i+1][0]-0.8, 7), xytext=(reg_steps[i][0]+0.8, 7),
                    arrowprops=dict(arrowstyle='->', color='#3498db', lw=1.5))
    
    # Row 2 - Bike Inquiry
    ax.text(1, 5, 'Bike Inquiry Flow', fontsize=12, fontweight='bold', color='#27ae60')
    bike_steps = [
        (1, 4, '"Show\nBikes"'),
        (4, 4, 'AI\nProcesses'),
        (7, 4, 'Fetch\nInventory'),
        (10, 4, 'Generate\nResponse'),
        (13, 4, 'EMI\nCalculation'),
        (16, 4, 'Voice/Text\nResponse')
    ]
    for x, y, text in bike_steps:
        box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, boxstyle="round,pad=0.05",
                             facecolor='#e8fce8', edgecolor='#27ae60', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8, ha='center', va='center', fontweight='bold')
    for i in range(5):
        ax.annotate('', xy=(bike_steps[i+1][0]-0.8, 4), xytext=(bike_steps[i][0]+0.8, 4),
                    arrowprops=dict(arrowstyle='->', color='#27ae60', lw=1.5))
    
    # Row 3 - Test Ride Booking
    ax.text(1, 2, 'Test Ride Booking Flow', fontsize=12, fontweight='bold', color='#e67e22')
    book_steps = [
        (1, 1, '"Book\nTest Ride"'),
        (4, 1, 'Collect\nDetails'),
        (7, 1, 'CRM\nEntry'),
        (10, 1, 'Send\nEmail/SMS'),
        (13, 1, 'Booking\nConfirmed'),
        (16, 1, 'Booking\nID ✓')
    ]
    for x, y, text in book_steps:
        box = FancyBboxPatch((x-0.8, y-0.5), 1.6, 1, boxstyle="round,pad=0.05",
                             facecolor='#fce8dc', edgecolor='#e67e22', linewidth=1.5)
        ax.add_patch(box)
        ax.text(x, y, text, fontsize=8, ha='center', va='center', fontweight='bold')
    for i in range(5):
        ax.annotate('', xy=(book_steps[i+1][0]-0.8, 1), xytext=(book_steps[i][0]+0.8, 1),
                    arrowprops=dict(arrowstyle='->', color='#e67e22', lw=1.5))
    
    plt.tight_layout()
    return fig

def main():
    """Generate all workflow diagrams"""
    print("Generating EveryLingua AI Workflow Diagrams...")
    
    # Main architecture diagram
    print("Creating main architecture diagram...")
    fig1 = create_workflow_diagram()
    fig1.savefig('workflow_architecture.png', dpi=150, bbox_inches='tight', 
                 facecolor='white', edgecolor='none')
    print("✓ Saved: workflow_architecture.png")
    
    # Chat workflow diagram
    print("Creating chat workflow diagram...")
    fig2 = create_chat_workflow_diagram()
    fig2.savefig('workflow_chat.png', dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    print("✓ Saved: workflow_chat.png")
    
    # User journey diagram
    print("Creating user journey diagram...")
    fig3 = create_user_journey_diagram()
    fig3.savefig('workflow_user_journey.png', dpi=150, bbox_inches='tight',
                 facecolor='white', edgecolor='none')
    print("✓ Saved: workflow_user_journey.png")
    
    plt.close('all')
    print("\n✅ All workflow diagrams generated successfully!")
    print("\nGenerated files:")
    print("  1. workflow_architecture.png - System architecture overview")
    print("  2. workflow_chat.png - Chat/Voice workflow")
    print("  3. workflow_user_journey.png - User journey flows")

if __name__ == "__main__":
    main()
