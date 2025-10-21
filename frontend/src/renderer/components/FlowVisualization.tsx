/**
 * 执行流程可视化组件
 */
import React from 'react';

interface Step {
  tool: string;
  tool_input?: any;
  result: string;
  status?: 'pending' | 'running' | 'completed' | 'failed';
}

interface FlowVisualizationProps {
  steps: Step[];
  currentStep?: number;
}

const toolIcons: Record<string, string> = {
  app_control: '📱',
  file_operation: '📁',
  browser_control: '🌐',
  text_processing: '📝',
  media_control: '🎵',
  scene_manager: '🎬',
};

const toolNames: Record<string, string> = {
  app_control: '应用控制',
  file_operation: '文件操作',
  browser_control: '浏览器',
  text_processing: '文本处理',
  media_control: '多媒体',
  scene_manager: '场景管理',
};

export const FlowVisualization: React.FC<FlowVisualizationProps> = ({
  steps,
  currentStep = -1,
}) => {
  if (steps.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-8 h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <svg
            className="w-16 h-16 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
            />
          </svg>
          <p>执行步骤将显示在这里</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 h-full overflow-y-auto">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-800">📊 执行流程</h2>
        <p className="text-sm text-gray-500">
          共 {steps.length} 个步骤
        </p>
      </div>

      <div className="space-y-4">
        {steps.map((step, index) => {
          const icon = toolIcons[step.tool] || '🔧';
          const toolName = toolNames[step.tool] || step.tool;
          const isActive = index === currentStep;
          const isCompleted = index < currentStep || currentStep === -1;
          const status = step.status || (isCompleted ? 'completed' : isActive ? 'running' : 'pending');

          return (
            <div
              key={index}
              className={`
                relative p-4 rounded-lg border-2 transition-all
                ${
                  status === 'completed'
                    ? 'border-green-300 bg-green-50'
                    : status === 'running'
                    ? 'border-blue-400 bg-blue-50 shadow-md'
                    : status === 'failed'
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-200 bg-gray-50'
                }
              `}
            >
              {/* 步骤编号和图标 */}
              <div className="flex items-start space-x-3">
                <div
                  className={`
                    flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-lg
                    ${
                      status === 'completed'
                        ? 'bg-green-500 text-white'
                        : status === 'running'
                        ? 'bg-blue-500 text-white animate-pulse'
                        : status === 'failed'
                        ? 'bg-red-500 text-white'
                        : 'bg-gray-300 text-gray-600'
                    }
                  `}
                >
                  {status === 'completed' ? '✓' : status === 'failed' ? '✗' : index + 1}
                </div>

                <div className="flex-1">
                  {/* 工具名称 */}
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-2xl">{icon}</span>
                    <h3 className="font-semibold text-gray-800">{toolName}</h3>
                    {status === 'running' && (
                      <span className="text-xs text-blue-600 font-medium">
                        执行中...
                      </span>
                    )}
                  </div>

                  {/* 工具输入 */}
                  {step.tool_input && (
                    <div className="mb-2 p-2 bg-white rounded border border-gray-200">
                      <p className="text-xs text-gray-500 mb-1">参数:</p>
                      <code className="text-xs text-gray-700">
                        {JSON.stringify(step.tool_input, null, 2)}
                      </code>
                    </div>
                  )}

                  {/* 执行结果 */}
                  {step.result && (
                    <div
                      className={`
                        p-2 rounded
                        ${
                          status === 'completed'
                            ? 'bg-green-100 text-green-800'
                            : status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-blue-100 text-blue-800'
                        }
                      `}
                    >
                      <p className="text-sm">{step.result}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* 连接线 */}
              {index < steps.length - 1 && (
                <div className="absolute left-8 top-full w-0.5 h-4 bg-gray-300" />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

