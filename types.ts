
export interface EmbyCover {
  id: string;
  name: string;
  url: string;
  videoUrl?: string;
  type: 'poster' | 'folder' | 'backdrop' | 'dynamic';
  aspectRatio: string;
  createdAt: number;
  dominantColor?: string;
}

export interface GenerationSettings {
  prompt: string;
  aspectRatio: '1:1' | '2:3' | '16:9';
  style: string;
  folderName: string;
  isDynamic: boolean;
}

export enum AppState {
  IDLE = 'IDLE',
  GENERATING = 'GENERATING',
  ERROR = 'ERROR'
}
