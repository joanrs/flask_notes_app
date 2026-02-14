// static/js/notes_keep.js

// Obtener datos de Flask desde los elementos JSON
function getNotesData() {
    try {
        const notesElement = document.getElementById('notes-data');
        const categoriesElement = document.getElementById('categories-data');

        if (!notesElement || !categoriesElement) {
            console.error('No se encontraron los datos en el HTML');
            return { notes: [], categories: [] };
        }

        const notesData = JSON.parse(notesElement.textContent);
        const categoriesData = JSON.parse(categoriesElement.textContent);

        // Normalizar datos de notas
        const notesList = Array.isArray(notesData) ? notesData : (notesData.items || []);

        return {
            notes: notesList,
            categories: categoriesData
        };
    } catch (error) {
        console.error('Error al parsear datos:', error);
        return { notes: [], categories: [] };
    }
}

// Inicializar la aplicación Vue
function initNotesApp() {
    const { createApp, ref, computed } = Vue;

    // Obtener datos
    const { notes: notesList, categories: categoriesList } = getNotesData();

    createApp({
        setup() {
            // Datos reactivos
            const notes = ref(notesList);
            const categories = ref(categoriesList);
            const searchQuery = ref('');
            const selectedCategory = ref('');
            const sortBy = ref('date');
            const noteToDelete = ref(null);
            let deleteModal = null;

            // Funciones auxiliares
            const isImage = (filename) => {
                const ext = filename.split('.').pop().toLowerCase();
                return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(ext);
            };

            const getExtension = (filename) => {
                const ext = filename.split('.').pop().toLowerCase();
                return ext.length > 3 ? ext.substring(0, 3) : ext;
            };

            const getFileIcon = (filename) => {
                const ext = filename.split('.').pop().toLowerCase();
                if (ext === 'pdf') return 'fas fa-file-pdf text-danger';
                if (['doc', 'docx'].includes(ext)) return 'fas fa-file-word text-primary';
                if (['xls', 'xlsx'].includes(ext)) return 'fas fa-file-excel text-success';
                if (['ppt', 'pptx'].includes(ext)) return 'fas fa-file-powerpoint text-warning';
                if (['zip', 'rar', 'tar', 'gz'].includes(ext)) return 'fas fa-file-archive text-secondary';
                if (['txt', 'md', 'rtf'].includes(ext)) return 'fas fa-file-alt text-secondary';
                if (['mp3', 'wav', 'ogg'].includes(ext)) return 'fas fa-file-audio text-info';
                if (['mp4', 'avi', 'mov', 'mkv'].includes(ext)) return 'fas fa-file-video text-danger';
                return 'fas fa-file';
            };

            const hexToRgba = (hex, alpha = 0.2) => {
                if (!hex) return `rgba(255, 255, 255, ${alpha})`;
                // Remove '#' if present
                hex = hex.replace('#', '');

                // Parse hex
                let r = 0, g = 0, b = 0;
                if (hex.length === 3) {
                    r = parseInt(hex[0] + hex[0], 16);
                    g = parseInt(hex[1] + hex[1], 16);
                    b = parseInt(hex[2] + hex[2], 16);
                } else if (hex.length === 6) {
                    r = parseInt(hex.substring(0, 2), 16);
                    g = parseInt(hex.substring(2, 4), 16);
                    b = parseInt(hex.substring(4, 6), 16);
                }

                return `rgba(${r}, ${g}, ${b}, ${alpha})`;
            };

            // Notas filtradas y ordenadas
            const filteredNotes = computed(() => {
                let filtered = [...notes.value];

                // Filtrar por búsqueda
                if (searchQuery.value.trim()) {
                    const query = searchQuery.value.toLowerCase().trim();
                    filtered = filtered.filter(note =>
                        (note.title && note.title.toLowerCase().includes(query)) ||
                        (note.content && note.content.toLowerCase().includes(query))
                    );
                }

                // Filtrar por categoría
                if (selectedCategory.value) {
                    filtered = filtered.filter(note =>
                        note.category_id == selectedCategory.value
                    );
                }

                // Ordenar
                filtered.sort((a, b) => {
                    if (sortBy.value === 'title') {
                        return (a.title || '').localeCompare(b.title || '');
                    }
                    if (sortBy.value === 'likes') {
                        return (b.likes_count || 0) - (a.likes_count || 0);
                    }
                    // Orden por fecha (predeterminado)
                    const dateA = new Date(a.updated_at || a.created_at || 0);
                    const dateB = new Date(b.updated_at || b.created_at || 0);
                    return dateB - dateA;
                });

                return filtered;
            });

            // Navegar a nota
            const viewNote = (id) => {
                if (id) {
                    window.location.href = `/notes/${id}`;
                }
            };

            // Confirmar eliminación
            const confirmDelete = (note) => {
                if (!note) return;

                noteToDelete.value = note;
                deleteModal = new bootstrap.Modal(document.getElementById('deleteModal'));
                deleteModal.show();
            };

            // Eliminar nota
            const deleteNote = async () => {
                if (!noteToDelete.value) return;

                try {
                    const response = await fetch(`/notes/${noteToDelete.value.id}/delete`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (response.ok) {
                        // Eliminar de la lista
                        notes.value = notes.value.filter(n => n.id !== noteToDelete.value.id);

                        // Cerrar modal
                        if (deleteModal) {
                            deleteModal.hide();
                        }

                        // Mostrar notificación (opcional)
                        showNotification('Note deleted successfully', 'success');
                    } else {
                        throw new Error('Failed to delete note');
                    }
                } catch (error) {
                    console.error('Error deleting note:', error);
                    showNotification('Error deleting note', 'error');
                }
            };

            // Dar like a nota
            const toggleLike = async (note) => {
                if (!note || !note.id) return;

                try {
                    const response = await fetch(`/notes/${note.id}/like`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });

                    if (response.ok) {
                        // Actualizar contador de likes
                        if (typeof note.likes_count === 'undefined') {
                            note.likes_count = 0;
                        }
                        note.likes_count += 1;

                        // Forzar actualización de Vue
                        notes.value = [...notes.value];
                    }
                } catch (error) {
                    console.error('Error liking note:', error);
                }
            };

            // Mostrar notificación
            const showNotification = (message, type = 'info') => {
                // Crear elemento de notificación
                const notification = document.createElement('div');
                notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
                notification.style.cssText = `
                    top: 20px;
                    right: 20px;
                    z-index: 9999;
                    min-width: 300px;
                `;
                notification.innerHTML = `
                    ${message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;

                document.body.appendChild(notification);

                // Auto-eliminar después de 5 segundos
                setTimeout(() => {
                    if (notification.parentNode) {
                        notification.remove();
                    }
                }, 5000);
            };

            // Exponer funciones y datos al template
            return {
                notes,
                categories,
                searchQuery,
                selectedCategory,
                sortBy,
                filteredNotes,
                noteToDelete,
                viewNote,
                confirmDelete,
                deleteNote,
                toggleLike,
                isImage,
                getFileIcon,
                getExtension,
                hexToRgba
            };
        }
    }).mount('#app');
}

// Esperar a que Vue esté disponible
if (typeof Vue !== 'undefined') {
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initNotesApp);
    } else {
        initNotesApp();
    }
} else {
    console.error('Vue.js no está cargado. Asegúrate de incluir Vue.js antes de este script.');
}