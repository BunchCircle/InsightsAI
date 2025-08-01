export async function cleanupCharts() {
    try {
        await fetch('/api/cleanup/reload', {
            method: 'POST',
        });
    } catch (error) {
        console.error('Error cleaning up charts:', error);
    }
}
