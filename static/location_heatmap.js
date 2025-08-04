// Enhanced visualization with location heatmaps
// location_heatmap.js

class DefectLocationVisualizer {
    constructor() {
        this.map = null;
        this.heatmapLayer = null;
        this.defectMarkers = [];
    }

    initializeMap(containerId, defaultLat = 40.7128, defaultLng = -74.0060) {
        // Initialize Leaflet map
        this.map = L.map(containerId).setView([defaultLat, defaultLng], 13);
        
        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);
        
        return this.map;
    }

    createDefectHeatmap(defectsData) {
        // Extract location keywords from defect sentences
        const locationData = this.extractLocationData(defectsData);
        
        if (locationData.length === 0) {
            return this.createFloorPlanHeatmap(defectsData);
        }
        
        // Create heatmap points
        const heatmapData = locationData.map(item => [
            item.lat, 
            item.lng, 
            item.intensity
        ]);
        
        // Add heatmap layer
        this.heatmapLayer = L.heatLayer(heatmapData, {
            radius: 25,
            blur: 15,
            maxZoom: 17,
            gradient: {
                0.2: 'blue',
                0.4: 'lime', 
                0.6: 'yellow',
                0.8: 'orange',
                1.0: 'red'
            }
        }).addTo(this.map);
        
        return this.heatmapLayer;
    }

    createFloorPlanHeatmap(defectsData) {
        // Create a building floor plan style heatmap
        const container = document.getElementById('floorPlanHeatmap');
        if (!container) return null;
        
        // Building areas mapping
        const buildingAreas = {
            'basement': { x: 50, y: 300, color: '#FF6B6B' },
            'foundation': { x: 100, y: 280, color: '#FF8E53' },
            'kitchen': { x: 200, y: 150, color: '#4ECDC4' },
            'bathroom': { x: 300, y: 100, color: '#45B7D1' },
            'electrical': { x: 150, y: 200, color: '#FFA726' },
            'exterior': { x: 50, y: 50, color: '#AB47BC' },
            'roof': { x: 200, y: 20, color: '#5C6BC0' }
        };
        
        // Count defects by area
        const areaCounts = {};
        defectsData.forEach(defect => {
            const area = this.identifyArea(defect.sentence);
            areaCounts[area] = (areaCounts[area] || 0) + 1;
        });
        
        // Create SVG visualization
        const svg = d3.select(container)
            .append('svg')
            .attr('width', 400)
            .attr('height', 350)
            .style('border', '1px solid #ddd')
            .style('border-radius', '8px');
        
        // Add building outline
        svg.append('rect')
            .attr('x', 20)
            .attr('y', 20)
            .attr('width', 360)
            .attr('height', 310)
            .attr('fill', 'none')
            .attr('stroke', '#333')
            .attr('stroke-width', 2);
        
        // Add area circles with defect counts
        Object.entries(areaCounts).forEach(([area, count]) => {
            const areaData = buildingAreas[area];
            if (areaData) {
                const radius = Math.max(10, count * 8);
                const opacity = Math.min(1, count / 5);
                
                svg.append('circle')
                    .attr('cx', areaData.x)
                    .attr('cy', areaData.y)
                    .attr('r', radius)
                    .attr('fill', areaData.color)
                    .attr('opacity', opacity)
                    .attr('stroke', '#fff')
                    .attr('stroke-width', 2);
                
                // Add count label
                svg.append('text')
                    .attr('x', areaData.x)
                    .attr('y', areaData.y + 5)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#fff')
                    .attr('font-weight', 'bold')
                    .attr('font-size', '12px')
                    .text(count);
                
                // Add area label
                svg.append('text')
                    .attr('x', areaData.x)
                    .attr('y', areaData.y + 35)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#333')
                    .attr('font-size', '10px')
                    .text(area.charAt(0).toUpperCase() + area.slice(1));
            }
        });
        
        return svg;
    }

    identifyArea(sentence) {
        const sentence_lower = sentence.toLowerCase();
        
        if (sentence_lower.includes('basement')) return 'basement';
        if (sentence_lower.includes('foundation')) return 'foundation';
        if (sentence_lower.includes('kitchen')) return 'kitchen';
        if (sentence_lower.includes('bathroom')) return 'bathroom';
        if (sentence_lower.includes('electrical') || sentence_lower.includes('wiring')) return 'electrical';
        if (sentence_lower.includes('exterior') || sentence_lower.includes('outside')) return 'exterior';
        if (sentence_lower.includes('roof') || sentence_lower.includes('ceiling')) return 'roof';
        
        return 'general';
    }

    extractLocationData(defectsData) {
        // This would extract GPS coordinates if available in the data
        // For demo purposes, return empty array to use floor plan instead
        return [];
    }

    addDefectMarker(lat, lng, defectData) {
        const marker = L.marker([lat, lng])
            .bindPopup(`
                <strong>${defectData.type}</strong><br>
                Severity: ${defectData.severity}<br>
                ${defectData.sentence.substring(0, 100)}...
            `)
            .addTo(this.map);
        
        this.defectMarkers.push(marker);
        return marker;
    }

    clearVisualization() {
        if (this.heatmapLayer) {
            this.map.removeLayer(this.heatmapLayer);
        }
        
        this.defectMarkers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.defectMarkers = [];
    }
}

// Usage function
function initializeLocationVisualization(defectsData, containerId) {
    const visualizer = new DefectLocationVisualizer();
    
    // Try to create floor plan heatmap first
    const heatmap = visualizer.createFloorPlanHeatmap(defectsData);
    
    return visualizer;
}
