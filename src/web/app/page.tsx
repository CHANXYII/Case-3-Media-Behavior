import Nav from "@/components/Nav";
import Hero from "@/components/Hero";
import RawData from "@/components/RawData";
import Cleaning from "@/components/Cleaning";
import FeatureSelection from "@/components/FeatureSelection";
import Personas from "@/components/Personas";
import PerClusterDrivers from "@/components/PerClusterDrivers";
import Predictor from "@/components/Predictor";
import MarketingPlan from "@/components/MarketingPlan";
import Footer from "@/components/Footer";
import BrandBand from "@/components/BrandBand";
import { ScrollProgress } from "@/components/Motion";
import ScrollCTA from "@/components/ScrollCTA";

export default function Page() {
  return (
    <main className="relative">
      <ScrollProgress />
      <ScrollCTA />
      <Nav />
      <Hero />
      <RawData />
      <Cleaning />
      <FeatureSelection />
      <Personas />
      <BrandBand />
      <PerClusterDrivers />
      <Predictor />
      <MarketingPlan />
      <Footer />
    </main>
  );
}
