'use client'

import { NextPage } from 'next';
import React, { useState } from 'react';

const UploadPage: NextPage = () => {
    const [fileName, setFileName] = useState<string>('');

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files ? event.target.files[0] : null;
        if (file) {
            setFileName(file.name);
        }
    };

    const [uploadProgress, setUploadProgress] = useState<number>(0);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
      
        const fileInput = document.getElementById('dropzone-file') as HTMLInputElement;
        if (fileInput?.files?.[0]) {
          const file = fileInput.files[0];
          const formData = new FormData();
          formData.append('file', file);
      
          const xhr = new XMLHttpRequest();
      
          // Listen for `upload.progress` event
          xhr.upload.onprogress = (event) => {
            if (event.lengthComputable) {
              const percent = (event.loaded / event.total) * 100;
              setUploadProgress(Math.round(percent));
            }
          };
      
          // Set up the request
          xhr.open('POST', '/api/upload', true);
      
          // Set up a handler for when the request finishes
          xhr.onload = () => {
            if (xhr.status === 200) {
              console.log('File uploaded successfully');
      
              // Reset the form and state
              setFileName('');
              setUploadProgress(0);
              fileInput.value = ''; // Reset file input
      
              // Optionally, show a success message
              alert('File uploaded successfully!');
            } else {
              console.error('Error in file upload');
              // Handle error
            }
          };
      
          // Send the request
          xhr.send(formData);
        }
    };
      

    return (
        <form onSubmit={handleSubmit}>
          <div className="flex items-center justify-center w-full pl-[25%] pr-[25%]">
            <label htmlFor="dropzone-file" className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-bray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg class="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                </svg>
                <p class="mb-2 text-sm text-gray-500 dark:text-gray-400"><span class="font-semibold">Click to upload</span> or drag and drop</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{fileName || 'TXT, DOCX, PDF or XLSX (MAX 100MB)'}</p>
              </div>
              <input id="dropzone-file" type="file" name="file" className="hidden" onChange={handleFileChange} required />
            </label>
          </div> 
    
          <div className="flex items-center justify-center pt-8">
            <button type="submit" className="btn btn-outline">Upload</button>
          </div>

          <div className="flex items-center justify-center pt-8">
            <progress className="progress w-56" value={uploadProgress} max="100"></progress>
          </div>
        </form>
    );
};

export default UploadPage;
