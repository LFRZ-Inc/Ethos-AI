import React, { useState } from 'react';
import { AlertTriangle, Trash2, X, Shield } from 'lucide-react';

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  conversation: {
    id: string;
    title: string;
    message_count: number;
    updated_at: string;
  };
}

const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  conversation
}) => {
  const [step, setStep] = useState(1);
  const [confirmationText, setConfirmationText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  const handleConfirm = async () => {
    if (step === 1) {
      setStep(2);
    } else if (step === 2) {
      setStep(3);
    } else if (step === 3 && confirmationText === 'DELETE') {
      setIsDeleting(true);
      try {
        await onConfirm();
        onClose();
      } catch (error) {
        console.error('Error deleting conversation:', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const handleClose = () => {
    setStep(1);
    setConfirmationText('');
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4 shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="text-red-500" size={20} />
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
              Delete Conversation
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            <X size={20} />
          </button>
        </div>

        {/* Step 1: Initial Warning */}
        {step === 1 && (
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Shield className="text-red-500 mt-1" size={20} />
                <div>
                  <h3 className="font-medium text-red-800 dark:text-red-200">
                    Permanent Deletion Warning
                  </h3>
                  <p className="text-sm text-red-600 dark:text-red-300 mt-1">
                    This action will permanently delete the conversation from Ethos AI's memory. 
                    Ethos will no longer remember this conversation or be able to reference it in future chats.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                Conversation Details
              </h4>
              <div className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <p><strong>Title:</strong> {conversation.title}</p>
                <p><strong>Messages:</strong> {conversation.message_count}</p>
                <p><strong>Last Updated:</strong> {conversation.updated_at}</p>
              </div>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400">
              Are you sure you want to continue with the deletion process?
            </p>
          </div>
        )}

        {/* Step 2: Final Warning */}
        {step === 2 && (
          <div className="space-y-4">
            <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <AlertTriangle className="text-orange-500 mt-1" size={20} />
                <div>
                  <h3 className="font-medium text-orange-800 dark:text-orange-200">
                    Final Confirmation
                  </h3>
                  <p className="text-sm text-orange-600 dark:text-orange-300 mt-1">
                    You are about to permanently delete this conversation from Ethos AI's memory. 
                    This action cannot be undone.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                What will be lost:
              </h4>
              <ul className="text-sm text-gray-600 dark:text-gray-300 space-y-1">
                <li>• All conversation messages</li>
                <li>• Context and memory of this conversation</li>
                <li>• Ability for Ethos to reference this conversation</li>
                <li>• Any insights or analysis from this conversation</li>
              </ul>
            </div>

            <p className="text-sm text-gray-600 dark:text-gray-400">
              Click "Continue" to proceed to the final confirmation step.
            </p>
          </div>
        )}

        {/* Step 3: Type DELETE */}
        {step === 3 && (
          <div className="space-y-4">
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <Trash2 className="text-red-500 mt-1" size={20} />
                <div>
                  <h3 className="font-medium text-red-800 dark:text-red-200">
                    Final Step
                  </h3>
                  <p className="text-sm text-red-600 dark:text-red-300 mt-1">
                    To confirm deletion, please type "DELETE" exactly as shown below.
                  </p>
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                Type "DELETE" to confirm:
              </label>
              <input
                type="text"
                value={confirmationText}
                onChange={(e) => setConfirmationText(e.target.value)}
                placeholder="DELETE"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-red-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                autoFocus
              />
            </div>

            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3">
              <p className="text-xs text-gray-600 dark:text-gray-400">
                <strong>Note:</strong> This is case-sensitive. You must type "DELETE" exactly as shown.
              </p>
            </div>
          </div>
        )}

        {/* Footer */}
        <div className="flex justify-end space-x-3 mt-6">
          <button
            onClick={handleClose}
            disabled={isDeleting}
            className="px-4 py-2 text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 rounded-md hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={handleConfirm}
            disabled={
              isDeleting || 
              (step === 3 && confirmationText !== 'DELETE')
            }
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isDeleting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <span>Deleting...</span>
              </>
            ) : (
              <>
                <Trash2 size={16} />
                <span>
                  {step === 1 ? 'Continue' : step === 2 ? 'Proceed' : 'Delete Permanently'}
                </span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal; 