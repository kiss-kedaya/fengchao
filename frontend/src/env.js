// 为了兼容从process.env到import.meta.env的过渡
// 这个文件可以在需要使用环境变量的地方引入

// 将Vite的环境变量导出为一个兼容的对象
export const processEnv = {
  NODE_ENV: import.meta.env.MODE,
  BASE_URL: import.meta.env.BASE_URL || '',
  // 添加更多需要的环境变量
  ...import.meta.env
};

// 如果你想在全局提供process.env
// 注意：这不是推荐的做法，但对于快速修复可能有用
if (typeof window !== 'undefined' && !window.process) {
  window.process = { env: processEnv };
}

export default processEnv; 