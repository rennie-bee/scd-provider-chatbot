import Image from 'next/image'
import UploadPage from './components/upload/page'

export default function Home() {
  return (
    <main>
      <h1 className="text-center text-4xl pt-6 pb-10 font-sans font-extrabold">Admin Portal</h1>
      <UploadPage></UploadPage>
    </main>
  )
}
