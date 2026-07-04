import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'album' },
  {
    path: 'album',
    loadChildren: () => import('./features/album/album.routes').then((m) => m.ALBUM_ROUTES),
  },
  { path: '**', redirectTo: 'album' },
];
