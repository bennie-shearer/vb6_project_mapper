"""
Mermaid.js Integration Module
Handles the loading, rendering, and error handling for Mermaid diagrams
"""


def add_enhanced_mermaid_script(f):
    """Add improved Mermaid script loading with better error handling"""

    f.write("""
    <!-- Mermaid initialization with robust error handling -->
    <script type="module">
        // Load Mermaid with fallback options
        async function loadMermaid() {
            try {
                // First attempt - primary CDN
                return await import('https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.esm.min.mjs');
            } catch (e) {
                console.warn("Primary CDN failed, trying fallback", e);
                try {
                    // Fallback CDN
                    return await import('https://unpkg.com/mermaid@10.6.1/dist/mermaid.esm.min.mjs');
                } catch (e2) {
                    console.error("All Mermaid CDNs failed", e2);
                    throw new Error("Failed to load Mermaid");
                }
            }
        }

        window.addEventListener('load', async function() {
            try {
                // Load Mermaid
                const mermaidModule = await loadMermaid();
                window.mermaid = mermaidModule.default;

                // Configure for better performance with large diagrams
                window.mermaid.initialize({
                    startOnLoad: false,
                    securityLevel: 'loose',
                    theme: 'default',
                    logLevel: 'error',
                    flowchart: {
                        useMaxWidth: true,
                        htmlLabels: true,
                        curve: 'basis',
                        diagramPadding: 8,
                        nodeSpacing: 60,
                        rankSpacing: 100
                    },
                    fontFamily: 'Arial, sans-serif',
                    fontSize: 12
                });

                // Initially render all visible diagrams with timeout protection
                const diagrams = document.querySelectorAll('.tab-content:not([style*="display: none"]) .mermaid');
                for (const diagram of diagrams) {
                    try {
                        await renderWithTimeout(diagram);
                    } catch (error) {
                        console.error("Error rendering diagram:", error);
                        showRenderError(diagram, error.message);
                    }
                }

                // Add rendering for tab changes
                const tabButtons = document.querySelectorAll('.tab-button');
                for (const button of tabButtons) {
                    button.addEventListener('click', async function() {
                        const tabId = this.getAttribute('onclick').match(/'([^']+)'/)[1];
                        const tabContent = document.getElementById(tabId);
                        const diagrams = tabContent.querySelectorAll('.mermaid');

                        for (const diagram of diagrams) {
                            // Only render if not already rendered
                            if (!diagram.querySelector('svg')) {
                                try {
                                    await renderWithTimeout(diagram);
                                } catch (error) {
                                    console.error("Error rendering diagram on tab change:", error);
                                    showRenderError(diagram, error.message);
                                }
                            }
                        }
                    });
                }
            } catch (error) {
                console.error("Failed to initialize Mermaid:", error);
                document.querySelectorAll('.mermaid').forEach(diagram => {
                    showRenderError(diagram, "Failed to load the diagram library. This might be due to network issues.");
                });
            }
        });

        // Render diagram with timeout protection
        async function renderWithTimeout(element) {
            return new Promise((resolve, reject) => {
                const timeoutId = setTimeout(() => {
                    reject(new Error("Diagram rendering timed out - diagram may be too complex"));
                }, 10000); // 10 second timeout

                try {
                    const id = 'mermaid-' + Math.random().toString(36).substr(2, 9);
                    window.mermaid.mermaidAPI.render(id, element.textContent)
                        .then(result => {
                            clearTimeout(timeoutId);
                            element.innerHTML = result.svg;

                            // Add zoom and pan controls to SVG
                            addDiagramControls(element);

                            resolve();
                        })
                        .catch(err => {
                            clearTimeout(timeoutId);
                            reject(err);
                        });
                } catch (error) {
                    clearTimeout(timeoutId);
                    reject(error);
                }
            });
        }

        // Show error message when rendering fails
        function showRenderError(element, message) {
            element.innerHTML = 
                '<div style="padding: 20px; background-color: #ffebee; border: 1px solid #f44336; border-radius: 5px;">' +
                '<h3 style="color: #d32f2f; margin-top: 0;">Diagram Rendering Error</h3>' +
                '<p>' + message + '</p>' +
                '<p>This might be because:</p>' +
                '<ul>' +
                '<li>The diagram has too many components and relationships</li>' +
                '<li>The browser has limited resources</li>' +
                '<li>Try using the Component Relationship Explorer instead</li>' +
                '</ul>' +
                '</div>';
        }

        // Add diagram controls (zoom, pan)
        function addDiagramControls(container) {
            const svgElement = container.querySelector('svg');
            if (!svgElement) return;

            let zoom = 1;
            let pan = { x: 0, y: 0 };
            let isDragging = false;
            let startPoint = { x: 0, y: 0 };

            // Create controls container with improved positioning
            const controlsContainer = document.createElement('div');
            controlsContainer.className = 'diagram-controls';
            controlsContainer.style.position = 'absolute';
            controlsContainer.style.top = '10px';
            controlsContainer.style.right = '10px';
            controlsContainer.style.zIndex = '1000'; // Ensure controls are above the diagram
            controlsContainer.style.padding = '5px';
            controlsContainer.style.borderRadius = '4px';
            controlsContainer.style.backgroundColor = 'rgba(255, 255, 255, 0.9)';
            controlsContainer.style.boxShadow = '0 1px 3px rgba(0,0,0,0.2)';

            // Add zoom controls with improved styling
            const zoomInButton = document.createElement('button');
            zoomInButton.textContent = '+';
            zoomInButton.title = 'Zoom In';
            zoomInButton.style.padding = '3px 8px';
            zoomInButton.style.marginRight = '4px';

            const zoomOutButton = document.createElement('button');
            zoomOutButton.textContent = '-';
            zoomOutButton.title = 'Zoom Out';
            zoomOutButton.style.padding = '3px 8px';
            zoomOutButton.style.marginRight = '4px';

            const resetButton = document.createElement('button');
            resetButton.textContent = 'Reset';
            resetButton.title = 'Reset View';
            resetButton.style.padding = '3px 8px';

            controlsContainer.appendChild(zoomInButton);
            controlsContainer.appendChild(zoomOutButton);
            controlsContainer.appendChild(resetButton);

            // Add padding to the container to make room for controls
            container.style.paddingTop = '40px';
            container.style.position = 'relative';
            container.appendChild(controlsContainer);

            // Make SVG draggable for panning
            svgElement.style.cursor = 'grab';

            svgElement.addEventListener('mousedown', function(e) {
                if (e.button === 0) { // Left mouse button
                    isDragging = true;
                    startPoint = { x: e.clientX, y: e.clientY };
                    svgElement.style.cursor = 'grabbing';
                    e.preventDefault();
                }
            });

            document.addEventListener('mousemove', function(e) {
                if (isDragging) {
                    const dx = e.clientX - startPoint.x;
                    const dy = e.clientY - startPoint.y;

                    pan.x += dx;
                    pan.y += dy;

                    startPoint = { x: e.clientX, y: e.clientY };
                    updateTransform();
                }
            });

            document.addEventListener('mouseup', function() {
                isDragging = false;
                svgElement.style.cursor = 'grab';
            });

            // Add button functionality
            zoomInButton.addEventListener('click', function() {
                zoom = Math.min(zoom + 0.1, 3); // Cap zoom at 3x
                updateTransform();
            });

            zoomOutButton.addEventListener('click', function() {
                zoom = Math.max(zoom - 0.1, 0.3); // Minimum zoom of 0.3x
                updateTransform();
            });

            resetButton.addEventListener('click', function() {
                zoom = 1;
                pan = { x: 0, y: 0 };
                updateTransform();
            });

            // Update transform function
            function updateTransform() {
                svgElement.style.transform = `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`;
                svgElement.style.transformOrigin = 'center';
            }
        }
    </script>
    """)
