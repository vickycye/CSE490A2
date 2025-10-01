document.addEventListener('DOMContentLoaded', function() {
    const processBtn = document.getElementById('processBtn');
    const enrichBtn = document.getElementById('enrichBtn');
    const inputText = document.getElementById('inputText');
    const entityList = document.getElementById('entityList');
    const relationshipsList = document.getElementById('relationshipsList');
    const graphSvg = document.getElementById('graphSvg');
    
    processBtn.addEventListener('click', processText);
    
    enrichBtn.addEventListener('click', function() {
        if (window.currentData) {
            enrichWithWikidata(window.currentData.entities, window.currentData.relationships);
        }
    });
    
    async function processText() {
        const text = inputText.value.trim();
        
        if (!text) {
            alert('Please enter some text');
            return;
        }
        
        try {
            const response = await fetch('/process', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text: text })
            });
            
            if (!response.ok) {
                throw new Error('Processing failed');
            }
            
            const data = await response.json();
            displayEntities(data.entities);
            displayRelationships(data.relationships);
            visualizeGraph(data.entities.unique_entities, data.relationships);
            
            // Store data for enrichment
            window.currentData = data;
            
            // Enable enrichment button
            const enrichBtn = document.getElementById('enrichBtn');
            if (enrichBtn) {
                enrichBtn.disabled = false;
            }
            
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while processing the text');
        }
    }

    async function enrichWithWikidata(entities, relationships) {
        try {
            const response = await fetch('/enrich', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    entities: entities.unique_entities,
                    relationships: relationships
                })
            });
            
            if (!response.ok) {
                throw new Error('Enrichment failed');
            }
            
            const data = await response.json();
            displayEnrichedEntities(data.enriched_entities);
            displayEnrichedRelationships(data.enriched_relationships);
            visualizeEnrichedGraph(data.enriched_entities, data.enriched_relationships);
            
        } catch (error) {
            console.error('Error enriching with Wikidata:', error);
            alert('An error occurred while enriching with Wikidata');
        }
    }
    
    function displayEntities(entities) {
        entityList.innerHTML = '';
        
        if (entities.unique_entities.length === 0) {
            entityList.innerHTML = '<p>No entities detected</p>';
            return;
        }
        
        entities.unique_entities.forEach(entity => {
            const div = document.createElement('div');
            div.className = 'entity-item';
            div.innerHTML = `
                <strong>${entity.text}</strong>
                <span class="entity-label">[${entity.label}]</span>
            `;
            entityList.appendChild(div);
        });
    }
    
    function displayRelationships(relationships) {
        relationshipsList.innerHTML = '';
        
        if (relationships.length === 0) {
            relationshipsList.innerHTML = '<p>No relationships detected</p>';
            return;
        }
        
        relationships.forEach(rel => {
            const div = document.createElement('div');
            div.className = 'relationship-item';
            div.textContent = `(${rel.subject}, ${rel.predicate}, ${rel.object})`;
            relationshipsList.appendChild(div);
        });
    }

    function displayEnrichedEntities(enrichedEntities) {
        entityList.innerHTML = '<h4>Wikidata-Enriched Entities</h4>';
        
        if (enrichedEntities.length === 0) {
            entityList.innerHTML += '<p>No entities enriched</p>';
            return;
        }
        
        enrichedEntities.forEach(entity => {
            const div = document.createElement('div');
            div.className = 'entity-item enriched';
            
            const wikidataLabel = entity.wikidata_label || entity.original_text;
            const qidLink = entity.qid ? 
                `<a href="https://www.wikidata.org/wiki/${entity.qid}" target="_blank">${entity.qid}</a>` : 
                'Not found';
            
            div.innerHTML = `
                <strong>${wikidataLabel}</strong>
                <div style="font-size: 0.9em; color: #666; margin-top: 4px;">
                    Original: ${entity.original_text}<br>
                    Wikidata: ${qidLink}
                    ${entity.description ? `<br><em>${entity.description}</em>` : ''}
                </div>
            `;
            entityList.appendChild(div);
        });
    }

    function displayEnrichedRelationships(enrichedRelationships) {
        relationshipsList.innerHTML = '<h4>Wikidata-Enriched Relationships</h4>';
        
        if (enrichedRelationships.length === 0) {
            relationshipsList.innerHTML += '<p>No relationships enriched</p>';
            return;
        }
        
        enrichedRelationships.forEach(rel => {
            const div = document.createElement('div');
            div.className = 'relationship-item enriched';
            
            const label = rel.wikidata_label || 'no relationship found';
            const propertyLink = rel.wikidata_property ? 
                `<a href="https://www.wikidata.org/wiki/Property:${rel.wikidata_property}" target="_blank">${rel.wikidata_property}</a>` :
                'N/A';
            
            div.innerHTML = `
                <strong>(${rel.subject}, ${label}, ${rel.object})</strong>
                <div style="font-size: 0.85em; color: #666; margin-top: 4px;">
                    Property: ${propertyLink}
                </div>
            `;
            relationshipsList.appendChild(div);
        });
    }
    
    function visualizeGraph(entities, relationships) {
        // Clear previous visualization
        graphSvg.innerHTML = '';
        
        if (entities.length === 0 && relationships.length === 0) {
            return;
        }
        
        const width = graphSvg.clientWidth;
        const height = graphSvg.clientHeight;
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Collect all unique nodes from entities and relationships
        const nodeSet = new Set();
        const entitySet = new Set();
        entities.forEach(entity => {
            nodeSet.add(entity.text);
            entitySet.add(entity.text);
        });
        relationships.forEach(rel => {
            nodeSet.add(rel.subject);
            nodeSet.add(rel.object);
        });
        
        const nodeArray = Array.from(nodeSet);
        
        // Calculate node degrees (in-degree + out-degree)
        const nodeDegrees = {};
        nodeArray.forEach(node => nodeDegrees[node] = 0);
        relationships.forEach(rel => {
            if (nodeDegrees[rel.subject] !== undefined) nodeDegrees[rel.subject]++;
            if (nodeDegrees[rel.object] !== undefined) nodeDegrees[rel.object]++;
        });
        
        // Sort nodes by degree (most connected first)
        const sortedNodes = nodeArray.slice().sort((a, b) => nodeDegrees[b] - nodeDegrees[a]);
        const maxDegree = Math.max(...Object.values(nodeDegrees), 1);
        
        // Create nodes with degree-based positioning and sizing
        const nodes = sortedNodes.map((nodeName, i) => {
            const numNodes = sortedNodes.length;
            const degree = nodeDegrees[nodeName];
            const normalizedDegree = degree / maxDegree; // 0 to 1
            
            // Size based on degree: 15-35 pixels radius
            const nodeRadius = 15 + normalizedDegree * 20;
            
            let x, y;
            
            if (numNodes <= 6) {
                // Small number: use circle
                const angle = (i * 2 * Math.PI) / numNodes - Math.PI / 2;
                // More popular nodes slightly closer to center
                const radius = Math.min(width, height) * 0.25 * (1 + (1 - normalizedDegree) * 0.5);
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
            } else if (numNodes <= 10) {
                // Medium number: spread spiral
                const angle = i * 2.4; // Golden angle
                const baseRadius = 60 + Math.sqrt(i) * 40;
                // More popular nodes closer to center
                const radius = baseRadius * (1 - normalizedDegree * 0.4);
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
                
                // Keep within bounds
                x = Math.max(70, Math.min(width - 70, x));
                y = Math.max(70, Math.min(height - 70, y));
            } else {
                // Many nodes: wide spiral with central clustering for popular nodes
                const angle = i * 2.4;
                const baseRadius = 80 + Math.sqrt(i) * 50; // More spread out
                // High-degree nodes much closer to center
                const radius = baseRadius * (1 - normalizedDegree * 0.6);
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
                
                // Keep within bounds with more padding
                x = Math.max(80, Math.min(width - 80, x));
                y = Math.max(80, Math.min(height - 80, y));
            }
            
            return {
                id: nodeName,
                label: nodeName,
                x: x,
                y: y,
                radius: nodeRadius,
                degree: degree,
                isEntity: entitySet.has(nodeName)
            };
        });
        
        // Create links from relationships
        const links = relationships.map(rel => ({
            source: rel.subject,
            target: rel.object,
            label: rel.predicate
        }));
        
        // Draw links
        links.forEach(link => {
            const sourceNode = nodes.find(n => n.id === link.source);
            const targetNode = nodes.find(n => n.id === link.target);
            
            if (sourceNode && targetNode) {
                // Calculate the angle and distance
                const dx = targetNode.x - sourceNode.x;
                const dy = targetNode.y - sourceNode.y;
                const angle = Math.atan2(dy, dx);
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Adjust line endpoints to stop at circle edges (using dynamic radius)
                const x1 = sourceNode.x + sourceNode.radius * Math.cos(angle);
                const y1 = sourceNode.y + sourceNode.radius * Math.sin(angle);
                const x2 = targetNode.x - targetNode.radius * Math.cos(angle);
                const y2 = targetNode.y - targetNode.radius * Math.sin(angle);
                
                // Draw arrow
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('class', 'link');
                line.setAttribute('stroke', '#999');
                line.setAttribute('stroke-width', '2');
                line.setAttribute('marker-end', 'url(#arrowhead)');
                graphSvg.appendChild(line);
                
                // Draw label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', (sourceNode.x + targetNode.x) / 2);
                text.setAttribute('y', (sourceNode.y + targetNode.y) / 2 - 5);
                text.setAttribute('class', 'link-label');
                text.setAttribute('text-anchor', 'middle');
                text.textContent = link.label;
                graphSvg.appendChild(text);
            }
        });
        
        // Draw nodes
        nodes.forEach(node => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'node');
            
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', node.x);
            circle.setAttribute('cy', node.y);
            circle.setAttribute('r', node.radius);
            
            // Use different styling for non-entity nodes (attributes like "Russian")
            if (!node.isEntity) {
                circle.setAttribute('fill', '#e8f4f8');
                circle.setAttribute('stroke', '#0097d4');
                circle.setAttribute('stroke-width', '2');
                circle.setAttribute('stroke-dasharray', '4,2');
            }
            
            g.appendChild(circle);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', node.x);
            text.setAttribute('y', node.y + node.radius + 15);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-size', Math.max(10, node.radius * 0.6) + 'px');
            text.textContent = node.label;
            g.appendChild(text);
            
            graphSvg.appendChild(g);
        });
        
        // Add arrowhead marker (make it more visible)
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead');
        marker.setAttribute('markerWidth', '12');
        marker.setAttribute('markerHeight', '12');
        marker.setAttribute('refX', '11');
        marker.setAttribute('refY', '6');
        marker.setAttribute('orient', 'auto');
        marker.setAttribute('markerUnits', 'userSpaceOnUse');
        
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 12 6, 0 12');
        polygon.setAttribute('fill', '#666');
        marker.appendChild(polygon);
        defs.appendChild(marker);
        graphSvg.insertBefore(defs, graphSvg.firstChild);
    }

    function visualizeEnrichedGraph(enrichedEntities, enrichedRelationships) {
        // Clear previous visualization
        graphSvg.innerHTML = '';
        
        if (enrichedEntities.length === 0) {
            return;
        }
        
        const width = graphSvg.clientWidth;
        const height = graphSvg.clientHeight;
        const centerX = width / 2;
        const centerY = height / 2;
        
        // Create nodes using Wikidata labels with degree-based layout
        const filteredEntities = enrichedEntities.filter(e => e.qid);
        
        // Calculate node degrees
        const nodeDegrees = {};
        filteredEntities.forEach(entity => nodeDegrees[entity.original_text] = 0);
        enrichedRelationships.forEach(rel => {
            if (nodeDegrees[rel.subject] !== undefined) nodeDegrees[rel.subject]++;
            if (nodeDegrees[rel.object] !== undefined) nodeDegrees[rel.object]++;
        });
        
        // Sort by degree
        const sortedEntities = filteredEntities.slice().sort((a, b) => 
            nodeDegrees[b.original_text] - nodeDegrees[a.original_text]
        );
        const maxDegree = Math.max(...Object.values(nodeDegrees), 1);
        
        const nodes = sortedEntities.map((entity, i) => {
            const numNodes = sortedEntities.length;
            const degree = nodeDegrees[entity.original_text];
            const normalizedDegree = degree / maxDegree;
            
            // Size based on degree
            const nodeRadius = 15 + normalizedDegree * 20;
            
            let x, y;
            
            if (numNodes <= 6) {
                const angle = (i * 2 * Math.PI) / numNodes - Math.PI / 2;
                const radius = Math.min(width, height) * 0.25 * (1 + (1 - normalizedDegree) * 0.5);
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
            } else if (numNodes <= 10) {
                const angle = i * 2.4;
                const baseRadius = 60 + Math.sqrt(i) * 40;
                const radius = baseRadius * (1 - normalizedDegree * 0.4);
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
                x = Math.max(70, Math.min(width - 70, x));
                y = Math.max(70, Math.min(height - 70, y));
            } else {
                const angle = i * 2.4;
                const baseRadius = 80 + Math.sqrt(i) * 50;
                const radius = baseRadius * (1 - normalizedDegree * 0.6);
                x = centerX + radius * Math.cos(angle);
                y = centerY + radius * Math.sin(angle);
                x = Math.max(80, Math.min(width - 80, x));
                y = Math.max(80, Math.min(height - 80, y));
            }
            
            return {
                id: entity.original_text,
                label: entity.wikidata_label || entity.original_text,
                qid: entity.qid,
                x: x,
                y: y,
                radius: nodeRadius,
                degree: degree
            };
        });
        
        // Create links from enriched relationships
        const links = enrichedRelationships
            .filter(rel => rel.wikidata_label)  // Only include relationships found on Wikidata
            .map(rel => ({
                source: rel.subject,
                target: rel.object,
                label: rel.wikidata_label
            }));
        
        // Draw links
        links.forEach(link => {
            const sourceNode = nodes.find(n => n.id === link.source);
            const targetNode = nodes.find(n => n.id === link.target);
            
            if (sourceNode && targetNode) {
                // Calculate the angle and distance
                const dx = targetNode.x - sourceNode.x;
                const dy = targetNode.y - sourceNode.y;
                const angle = Math.atan2(dy, dx);
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                // Adjust line endpoints to stop at circle edges (using dynamic radius)
                const x1 = sourceNode.x + sourceNode.radius * Math.cos(angle);
                const y1 = sourceNode.y + sourceNode.radius * Math.sin(angle);
                const x2 = targetNode.x - targetNode.radius * Math.cos(angle);
                const y2 = targetNode.y - targetNode.radius * Math.sin(angle);
                
                // Draw arrow
                const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                line.setAttribute('x1', x1);
                line.setAttribute('y1', y1);
                line.setAttribute('x2', x2);
                line.setAttribute('y2', y2);
                line.setAttribute('class', 'link');
                line.setAttribute('stroke', '#28a745');
                line.setAttribute('stroke-width', '3');
                line.setAttribute('marker-end', 'url(#arrowhead-enriched)');
                graphSvg.appendChild(line);
                
                // Draw label
                const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
                text.setAttribute('x', (sourceNode.x + targetNode.x) / 2);
                text.setAttribute('y', (sourceNode.y + targetNode.y) / 2 - 5);
                text.setAttribute('class', 'link-label');
                text.setAttribute('text-anchor', 'middle');
                text.setAttribute('fill', '#28a745');
                text.setAttribute('font-weight', 'bold');
                text.textContent = link.label;
                graphSvg.appendChild(text);
            }
        });
        
        // Draw nodes
        nodes.forEach(node => {
            const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
            g.setAttribute('class', 'node');
            g.style.cursor = 'pointer';
            g.onclick = () => window.open(`https://www.wikidata.org/wiki/${node.qid}`, '_blank');
            
            const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
            circle.setAttribute('cx', node.x);
            circle.setAttribute('cy', node.y);
            circle.setAttribute('r', node.radius);
            circle.setAttribute('fill', '#28a745');
            circle.setAttribute('stroke', '#fff');
            circle.setAttribute('stroke-width', Math.max(2, node.radius * 0.1));
            g.appendChild(circle);
            
            const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            text.setAttribute('x', node.x);
            text.setAttribute('y', node.y + node.radius + 15);
            text.setAttribute('text-anchor', 'middle');
            text.setAttribute('font-weight', 'bold');
            text.setAttribute('font-size', Math.max(10, node.radius * 0.6) + 'px');
            text.textContent = node.label;
            g.appendChild(text);
            
            graphSvg.appendChild(g);
        });
        
        // Add enriched arrowhead marker (make it more visible)
        const defs = graphSvg.querySelector('defs') || 
                     document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        const marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
        marker.setAttribute('id', 'arrowhead-enriched');
        marker.setAttribute('markerWidth', '12');
        marker.setAttribute('markerHeight', '12');
        marker.setAttribute('refX', '11');
        marker.setAttribute('refY', '6');
        marker.setAttribute('orient', 'auto');
        marker.setAttribute('markerUnits', 'userSpaceOnUse');
        
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '0 0, 12 6, 0 12');
        polygon.setAttribute('fill', '#28a745');
        marker.appendChild(polygon);
        defs.appendChild(marker);
        
        if (!graphSvg.querySelector('defs')) {
            graphSvg.insertBefore(defs, graphSvg.firstChild);
        }
    }
});