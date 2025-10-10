import api from './api'

export const fileService = {
  async uploadFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    
    return response.data
  },
}