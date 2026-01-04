
import React from 'react';

const Header: React.FC = () => {
  return (
    <div className="bg-[#075e54] text-white px-4 py-3 flex items-center justify-between shadow-md sticky top-0 z-50">
      <div className="flex items-center gap-3">
        <div className="relative">
          <div className="w-10 h-10 rounded-full bg-[#128c7e] flex items-center justify-center font-bold text-lg border border-white/20">
            S
          </div>
          <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-400 border-2 border-[#075e54] rounded-full"></div>
        </div>
        <div>
          <h1 className="font-bold text-lg leading-tight">Stilo</h1>
          <p className="text-xs text-green-100 italic">Consultor de Imagem Masculina</p>
        </div>
      </div>
      <div className="flex gap-4">
        <div className="text-[10px] bg-black/20 px-2 py-1 rounded border border-white/10 uppercase tracking-wider">
          V1.0 MVP
        </div>
      </div>
    </div>
  );
};

export default Header;
