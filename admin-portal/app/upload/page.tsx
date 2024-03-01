'use client'

import { getSignedURL } from '@/app/upload/getURL';
import { NextPage } from 'next';
import React, { useState, useRef, DragEvent } from 'react';

const allowedFileTypes = [
  "text/plain", // .txt
  "application/pdf", //.pdf
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", //.docx
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" //.xlsx
]

const maxFileSize = 1048576 * 1000 // 100 MB

const UploadPage: NextPage = () => {
    const [file, setFile] = useState<File | null>(null);
    const [fileName, setFileName] = useState<string>('');
    const [showModal, setShowModal] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<number>(0);
    const [isDragOver, setIsDragOver] = useState(false);
    const formRef = useRef<HTMLFormElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [modalMessage, setModalMessage] = useState('');

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
      const selectedFile = event.target.files ? event.target.files[0] : null;
      if (selectedFile) {
        processFile(selectedFile);
      }
      else {
        setFileName('');
      }
    };

    const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault(); // Prevent default behavior
      setIsDragOver(true);
    };
    
    const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);
    };
    
    const handleDrop = (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      setIsDragOver(false);

      const droppedFile = e.dataTransfer.files[0];
      if(droppedFile) {
        processFile(droppedFile);
      }
      else {
        setFileName('');
      }
    };

    const processFile = (selectedFile: File) => {
      console.log(selectedFile);
      if(!allowedFileTypes.includes(selectedFile.type)) {
        console.error("File type not allowed");
        handleUploadError("File Type Not Allowed");
        return;
      }
  
      if(selectedFile.size > maxFileSize) {
        console.error("File size too large");
        handleUploadError("File Size Too Large");
        return;
      }

      setFile(selectedFile);
      setFileName(selectedFile.name);
    };

    const unselectFile = () => {
        if (fileInputRef.current) {
            fileInputRef.current.value = '';  // Reset file input
        }
        setFile(null);
        setFileName('');  // Reset file name
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
      
        if (file) {
          const signedURLResult = await getSignedURL(file);
          if(signedURLResult.failure !== undefined) {
            console.error(signedURLResult.failure);
            handleUploadError("Get Pre-signed URL Failed");
            return;
          }

          const { url } = signedURLResult.success;
          console.log({url});

          try {
            // const formData = new FormData();
            // formData.append('file', file);
    
            const xhr = new XMLHttpRequest();
    
            xhr.upload.onprogress = (event) => {
                if (event.lengthComputable) {
                    const percent = (event.loaded / event.total) * 100;
                    setUploadProgress(Math.round(percent));
                }
            };
    
            xhr.onload = () => {
                if (xhr.status === 200) {
                    console.log('File uploaded successfully');
                    handleUploadSuccess();
                } else {
                    console.error('Error in file upload:', xhr.responseText);
                    handleUploadError("File Upload Failed");
                }
            };
    
            xhr.onerror = () => {
                console.error('Error in file upload');
                handleUploadError("File Upload Failed");
            };
    
            xhr.open('PUT', url, true);
            xhr.setRequestHeader("Content-Type", file.type);
            xhr.send(file);
          }
          catch (error) {
            console.error('Error: ', error);
            handleUploadError("File Upload Failed");
          }
        }
        else {
          console.error("No file selected");
          handleUploadError('No File Selected');
        }
    };

    const handleModalClose = () => {
        setShowModal(false); // Hide the modal
        setFileName(''); // Reset file name
        setFile(null); // Reset file
        setUploadProgress(0); // Reset progress
        if (formRef.current) {
          formRef.current.reset(); // Reset the form
        }
    };

    const handleUploadSuccess = () => {
      setModalMessage('File Upload Successful');
      setShowModal(true);
    };
    
    const handleUploadError = (errorMessage:string) => {
      setModalMessage(errorMessage);
      setShowModal(true);
    };
      

    return (
      <div>
        <form ref={formRef} onSubmit={handleSubmit}>
          {/* drag and drop zone */}
          <div onDrop={handleDrop} onDragOver={handleDragOver} onDragLeave={handleDragLeave} className="flex items-center justify-center w-full pl-[25%] pr-[25%]">
            <label htmlFor="dropzone-file" className={`flex flex-col items-center justify-center w-full h-80 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer ${
    isDragOver ? 'border-zinc-500' : 'border-gray-300'} bg-neutral-50  hover:bg-neutral-100`}>
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <svg className="w-8 h-8 mb-4 text-gray-500" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                </svg>
                <p className="mb-2 text-sm text-gray-500"><span className="font-semibold">Click to upload</span> or drag and drop</p>
                <p className="text-xs text-gray-500">{'TXT, DOCX, PDF or XLSX (MAX 100MB)'}</p>
              </div>
            </label>
            <input ref={fileInputRef} id="dropzone-file" type="file" name="file" className="hidden" onChange={handleFileChange} />
          </div>

          {/* file list and upload progress part */}
          {fileName && (
            <div className="flex items-center justify-center w-full pl-[25%] pr-[25%] mt-4 px-4">
              <div className="flex items-center w-full max-w-xl">
                <div className="flex items-center flex-1 min-w-0">
                  <span className="text-sm font-medium text-gray-800 truncate">
                    {fileName}
                  </span>
                  <button type="button" onClick={unselectFile} className="ml-2">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth="1.5" stroke="currentColor" className="w-6 h-6">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                    </svg>
                  </button>
                </div>
                <div className="w-32 ml-4">
                  <progress className="progress w-full" value={uploadProgress} max="100"></progress>
                </div>
              </div>
            </div>
          )}
    
          <div className="flex items-center justify-center pt-8">
            <button type="submit" className="btn btn-outline">Upload</button>
          </div>
        </form>

        {/* pop up modal showing customized message */}
        {showModal && (
          <>
            <div className="fixed inset-0 bg-opacity-75 transition-opacity z-40"></div>
            <div id="popup-modal" className="fixed inset-x-0 top-0 z-50 flex justify-center bg-opacity-50">
              <div className="relative p-4 w-full max-w-md h-auto bg-white rounded-lg shadow mt-4 mx-auto border-2 border-zinc-500/100">
                <div className="p-4 md:p-5 text-center">
                  <h3 className="mb-5 text-lg font-normal text-gray-500">{modalMessage}</h3>
                  <button onClick={handleModalClose} type="button" className="text-white bg-red-600 hover:bg-red-800 focus:ring-4 focus:outline-none focus:ring-red-300 font-medium rounded-lg text-sm inline-flex items-center px-5 py-2.5 text-center mr-2">
                    Close
                  </button>
                </div>
              </div>
            </div>
          </>
        )}
    </div>
    );
};

export default UploadPage;
