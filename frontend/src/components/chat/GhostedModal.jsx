import React from 'react';
import { X } from 'lucide-react';

const GhostedModal = ({ userName, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl max-w-sm w-full p-6">
        <div className="text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <X className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            No Response Received
          </h2>
          <p className="text-gray-600 text-sm mb-4">
            The timer expired without a response from {userName}.
          </p>
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-6">
            <p className="text-sm text-red-800 font-medium">
              Automatic -10% penalty applied
            </p>
          </div>
          <button
            onClick={onClose}
            className="w-full px-4 py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};

export default GhostedModal;
